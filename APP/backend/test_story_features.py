import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from APP.backend import database
from APP.backend import fetch_news, main
from APP.backend.story_text import clean_story_text, is_comic_available
from PanelPulse_v2 import comic


class StoryFeatureTests(unittest.TestCase):
    def test_story_text_is_unescaped_stripped_and_collapsed(self):
        self.assertEqual(
            clean_story_text("  &lt;p&gt;J&amp;K  &lt;/p&gt;  <b>News</b> "),
            "J&K News",
        )

    def test_comic_availability_uses_length_and_normalized_title(self):
        self.assertFalse(is_comic_available("Same, title!", "same title"))
        self.assertFalse(is_comic_available("Headline", "x" * 39))
        self.assertTrue(is_comic_available("Headline", "x" * 40))

    def test_fetch_cleans_text_without_changing_link_id(self):
        link = "https://example.com/story"
        entry = {
            "link": link,
            "title": "J&amp;K &lt;b&gt;news&lt;/b&gt;",
            "summary": "<p>  A  clean summary &amp; more. </p>",
        }
        with patch.object(
            fetch_news.feedparser,
            "parse",
            return_value=SimpleNamespace(entries=[entry]),
        ):
            story = fetch_news.fetch_headlines(limit=1)[0]

        self.assertEqual(story["title"], "J&K news")
        self.assertEqual(story["summary"], "A clean summary & more.")
        self.assertEqual(story["id"], hashlib.md5(link.encode()).hexdigest()[:10])

    def test_stories_route_adds_both_flags(self):
        database_stories = [
            {
                "id": "empty",
                "title": "No summary",
                "summary": "",
                "link": "",
            },
            {
                "id": "politics",
                "title": "Akhilesh discusses SP-Congress alliance",
                "summary": "Leaders discussed their alliance before the next election.",
                "link": "",
            },
            {
                "id": "tariffs",
                "title": "Tariffs may rise",
                "summary": "This report says trade costs could increase in the coming months.",
                "link": "",
            },
        ]
        with patch.object(main, "get_stories", return_value=database_stories):
            stories = main.read_stories()

        by_id = {story["id"]: story for story in stories}
        self.assertFalse(by_id["empty"]["comic_available"])
        self.assertTrue(by_id["politics"]["sensitive"])
        self.assertFalse(by_id["tariffs"]["sensitive"])
        self.assertTrue(by_id["tariffs"]["comic_available"])

    def test_sensitive_includes_serious_political_and_religious_stories(self):
        self.assertTrue(comic.is_sensitive("A truck crash", ""))
        self.assertTrue(comic.is_sensitive("Akhilesh discusses SP-Congress alliance", ""))
        self.assertTrue(comic.is_sensitive("Bulldozer near sacred Sheshnag lake", ""))
        self.assertFalse(comic.is_sensitive("Tariffs may rise", "Trade costs could increase."))

    def test_story_text_migration_is_idempotent(self):
        original_path = database.DATABASE_PATH
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                database.DATABASE_PATH = Path(temp_dir) / "stories.db"
                database.create_table()
                connection = database.get_connection()
                try:
                    connection.execute(
                        "INSERT INTO stories (id, title, summary) VALUES (?, ?, ?)",
                        ("story-1", "J&amp;K &lt;b&gt;news&lt;/b&gt;", "<p>  A  summary </p>"),
                    )
                    connection.commit()
                finally:
                    connection.close()

                self.assertEqual(database.migrate_story_text(), 1)
                self.assertEqual(database.migrate_story_text(), 0)
                connection = database.get_connection()
                try:
                    story = connection.execute(
                        "SELECT title, summary FROM stories WHERE id = ?",
                        ("story-1",),
                    ).fetchone()
                finally:
                    connection.close()
                self.assertEqual(story["title"], "J&K news")
                self.assertEqual(story["summary"], "A summary")
            finally:
                database.DATABASE_PATH = original_path


if __name__ == "__main__":
    unittest.main()