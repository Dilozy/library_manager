import json
import unittest

from app.main import Book, Library


def setUpModule():
    with open("tests/library.json", "w", encoding="utf-8") as test_file:
        data = [
            {"id": 0, "title": "Book1", "author": "Ivan Ivanov", "year": 2000},
            {"id": 1, "title": "Book2", "author": "Ivan Ivanov", "year": 2001},
            {"id": 2, "title": "Book3", "author": "Ivan Ivanov", "year": 2002},
            {"id": 3, "title": "Book4", "author": "Ivan Ivanov", "year": 2003},
            {"id": 4, "title": "Book5", "author": "Ivan Ivanov", "year": 2004},
        ]
        json.dump(data, test_file)


class BookClassTestCase(unittest.TestCase):
    """
    Класс, предназначенный для тестирования функционала класса Book
    """
    @classmethod
    def setUpClass(cls):
        with open("tests/library.json", encoding="utf-8") as test_file:
            data = json.load(test_file)
            cls.last_book_id = data[-1].get("id")

    def test_title_validation_with_invalid_titles(self):
        invalid_titles = ("A", "  ", "%%$#", "!12 стульев", "111", "11111")
        for title in invalid_titles:
            with self.subTest(title=title):
                with self.assertRaises(ValueError):
                    new_book = Book(2, title, "Ivan Ivanov", 1999)

    def test_title_validation_with_valid_titles(self):
        valid_titles = ("1491: New Revelations of the Americas Before Columbus", "1984", "12 стульев",
                        "If", "Книга1")
        for title in valid_titles:
            with self.subTest(title=title):
                try:
                    book = Book(1, title, "Author", 2023)
                except Exception as e:
                    self.fail(
                        f"Valid title '{title}' raised an exception: {e}")

    def test_author_validation_with_invalid_values(self):
        invalid_values = ("123", "F", "Fa", "Smith-", "John  Doe", "Jean -Pierre Bidou",
                          "Henry 'ONeil", "Jean--Pierre", "Henry O' Neil", "Ben")
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    new_book = Book(2, "Book", value, 1999)

    def test_author_validation_with_valid_values(self):
        valid_values = ("John Smith", "Jean-Pierre Smith", "Иван Петров", "Henry O'Neil"
                        "Александр Мамин-Сибиряк", "Jean-Claude Van Damme", "Li Bai", "Homer")
        for value in valid_values:
            with self.subTest(value=value):
                try:
                    book = Book(1, "Book", value, 2023)
                except Exception as e:
                    self.fail(
                        f"Valid value '{value}' raised an exception: {e}")

    def test_year_validation_with_invalid_values(self):
        invalid_years = (-100, 10000, 0.2, 2030, 0)
        for year in invalid_years:
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    new_book = Book(2, "Book", "Homer", year)

    def test_year_validation_with_valid_values(self):
        valid_years = (2024, 100, 1500, 1, 1000)
        for year in valid_years:
            with self.subTest(year=year):
                try:
                    book = Book(1, "Book", "Homer", year)
                except Exception as e:
                    self.fail(
                        f"Valid year '{year}' raised an exception: {e}")

    def test_unique_book_id(self):
        new_book = Book(self.last_book_id, "Book6", "Ivan Ivanov", 2005)

        self.assertEqual(new_book.id, self.last_book_id + 1)


class LibraryClassTestCase(unittest.TestCase):
    """
    Класс, предназначенный для тестирования функционала класса Library
    """

    def test_books_data_property(self):
        library = Library()
        with open("app/library.json", encoding="utf-8") as library_data:
            data = json.load(library_data)
        self.assertEqual(library.books_data, data)


if __name__ == "__main__":
    unittest.main()
