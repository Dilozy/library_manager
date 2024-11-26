import json
import re
from datetime import date
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Union, List


class NotFoundInTheLibrary(Exception):
    """
    Кастомное исключение для случаев, когда книга не найдена в библиотеке.
    """
    
    pass


class IncorrectSearchFields(Exception):
    """
    Кастомное исключение для случаев, когда при поиске по полю введены несуществующие поля.
    """
    
    pass

class AlreadyInTheLibrary(Exception):
    """
    Кастомное исключение для случаев, когда в библиотеку добавляется неуникальная книга
    """
    
    pass


class Book:
    """
    Класс для хранение информации о конкретной книги
    """
    
    __slots__ = ("_id", "_title", "_author", "_year", "_status")

    def __init__(self, last_added_book_id: int, title: str, author: str, year: int):
        # генерируем уникальный id для книги просто добавляя 1 к последнему номеру в библиотеке
        self._id = last_added_book_id + 1
        self._title = self._validate_title(title)
        self._author = self._validate_author(author)
        self._year = self._validate_year(year)
        self._status = "В наличии"

    def __str__(self):
        return f"{self._title} by {self._author}"


    def _validate_title(self, title: str) -> str:
        """
        Функция для валидации названия книги
        """
        regex = (
                    r"^[A-Za-zА-Яа-яЁё]{2}[A-Za-zА-Яа-яЁё0-9\s\.,;:!?()\'\"\-]*$"
                    r"|^\d{1,4}[A-Za-zА-Яа-яЁё\s\.,;:!?()\'\"\-]+$"
                    r"|^\d{4}$"
                )
        match = re.search(regex, title)
        
        if match and match.group(0) == title:
            return title.strip().title()
        raise ValueError("Недопустимое название книги")

    def _validate_year(self, year) -> int:
        """
        Функция для валидации года издания книги
        """
        try:
            year = int(year)
        except ValueError as exc:
            raise ValueError("Год должен быть целым числом.") from exc

        if year <= 0 or year > date.today().year:
            raise ValueError("Год должен быть положительным числом и не превышать текущий год.")
        
        return year

    def _validate_author(self, author: str) -> str:
        """
        Функция для валидации автора книги
        """
        regex = r"^[A-Za-zА-Яа-яЁё]{2,}(?:['\-\s][A-Za-zА-Яа-яЁё]+)+$|^[A-Za-zА-Яа-яЁё]{5,}$"
        match = re.search(regex, author)

        if match and match.group(0) == author:
            return author.strip().title()
        raise ValueError("Недопустимое имя автора. Ожидается строка с буквами, пробелами или дефисами.")
        
    @property
    def id(self) -> int:
        """Свойство для получения атрибута id."""
        return self._id

    @property
    def title(self) -> str:
        """Свойство для получения атрибута title."""
        return self._title

    @property
    def author(self) -> str:
        """Свойство для получения атрибута author."""
        return self._author

    @property
    def year(self) -> int:
        """Свойство для получения атрибута year."""
        return self._year

    @property
    def status(self) -> str:
        """Свойство для получения атрибута status."""
        return self._status

    def to_dict(self) -> Dict[str, Union[int, str]]:
        """
        Метод для преобразования данных из экзмепляра объекта Book в сериализируемый словарь(dict).
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "status": self.status,
        }


@dataclass
class Library:
    """
    Dataclass для хранения информации обо всех книгах в библиотеке.
    """
    
    _books_data: list = field(default_factory=list)

    def __post_init__(self):
        try:
            with open("app/library.json", encoding="utf-8") as books_in_library:
                self._books_data = json.load(books_in_library)
        
        except json.JSONDecodeError as e:
            print(f"Ошибка загрузки данных: {e}")
            self._books_data = []

        except FileNotFoundError: # создаем новый файл в случае, если библиотека еще не была создана
            with open("app/library.json", "w", encoding="utf-8") as books_in_library:
                json.dump([], books_in_library)

    @property
    def books_data(self) -> List[Dict]:
        """Свойство для получения атрибута books_data."""
        return self._books_data


class MenuOptions(Enum):
    """
    Класс-перечисление для опций взаимодействия с библиотекой при работе через консоль.
    """

    ADD_BOOK = ("1", "Добавить книгу")
    DELETE_BOOK = ("2", "Удалить книгу")
    CHANGE_STATUS = ("3", "Изменить статус книги")
    LIST_BOOKS = ("4", "Показать все книги")
    SEARCH_BOOKS = ("5", "Искать книги")
    EXIT = ("0", "Выход")


class LibraryManager:
    """
    Класс для обработки запросов к библиотеке.
    """
    
    def __init__(self):
        self.library = Library()

    @staticmethod
    def _update_data(books_data) -> None:
        """
        Статический метод для обновления данных в файле после внесенных изменений.
        """
        with open("app/library.json", "w", encoding="utf-8") as input_file:
            json.dump(books_data, input_file, indent=4, ensure_ascii=False)

    def _find_book_in_the_library(self, book_id: int, return_index: bool = False) -> Union[int, dict]:
        """
        Метод для поиска книги в библиотеке, основанный на алгоритме бинарного поиска
        Именованный параметр return_index используется, когда нам нужен не сам объект книги,
        а его индекс, например, для удаления.
        """
        low_bound = 0
        high_bound = len(self.library.books_data) - 1
        while low_bound <= high_bound:
            mid = (low_bound + high_bound) // 2
            if (target_book := self.library.books_data[mid].get("id")) == book_id:
                if return_index:
                    return mid
                return target_book
            if self.library.books_data[mid].get("id") > book_id:
                high_bound = mid - 1
            else:
                low_bound = mid + 1
        return -1

    def _add_book(self, title: str, author: str, year: int) -> None:
        """
        Метод для добавления новой книги в библиотеку.
        """
        try:
            if self.library.books_data:
                last_added_book_id = self.library.books_data[-1].get("id")
            else:
                last_added_book_id = 0 # на случай, если в библиотеке еще нет добавленных книг
            new_book = Book(last_added_book_id, title, author, year)
        except ValueError:
            raise
        
        # проверяем на уникальность добавляемой книги
        books_in_library_with_the_same_author = self._search_books_by(
                                                                        f"author = {new_book.author}",
                                                                        return_book_obj=True
                                                                        )
        if books_in_library_with_the_same_author:
            for book in books_in_library_with_the_same_author:
                if (book.get("title"), book.get("year")) == (new_book.title, new_book.year):
                    raise AlreadyInTheLibrary(
                        "Книга с такими автором, названием и годом издания уже существует в библиотеке"
                        )
        
        self.library.books_data.append(new_book.to_dict())

    def _delete_book(self, book_id: int):
        """
        Метод для удаления книги из библиотеки по заданному ID.
        """
        book_index = self._find_book_in_the_library(book_id, return_index=True)
        if book_index == -1:
            raise NotFoundInTheLibrary("Книга с таким идентификатором не найдена в библиотеке")
        
        self.library.books_data.pop(book_index)

    def _change_book_status(self, book_id: int) -> None:
        """
        Метод для изменения статуса книги.
        При вызове у книги со статусом "В наличии" меняет его на статус "Выдана".
        При вызове у книги со статусом "Выдана" меняет его на статус "В наличии".
        """
        book_index = self._find_book_in_the_library(book_id, return_index=True)
        if book_index == -1:
            raise NotFoundInTheLibrary("Книга с таким идентификатором не найдена в библиотеке")
        
        if self.library.books_data[book_index]["status"] == "В наличии":
            self.library.books_data[book_index]["status"] = "Выдана"
        else:
            self.library.books_data[book_index]["status"] = "В наличии"

    def _list_all_books(self) -> None:
        """
        Метод для вывода информации обо всех книгах.
        """
        header = f"{'ID':<4} | {'Title':<30} | {'Author':<20} | {'Year':<6} | {'Status':<10}"
        print(header)
        print("-" * len(header))
        
        for book in self.library.books_data:
            print(f"{book['id']:<4} | {book['title']:<30} | {book['author']:<20} | {book['year']:<6} | {book['status']:<10}")

    def _search_books_by(self, search_query: str, return_book_obj=False) -> None:
        """
        Метод для поиска книги по конкретному полю (title, author, year).
        Именованные параметр return_book_obj используется, когда необходимо вернуть сам объект книги,
        а не просто вывести результат
        """
        search_field, search_value = search_query.split(" = ")
        search_field = search_field.lower().strip()
        search_value = search_value.title().strip()
        
        if search_field not in ("title", "author", "year"):
            raise IncorrectSearchFields("Введено некорректное поле для поиска")

        search_results = [book for book in self.library.books_data if book.get(search_field) == search_value]
        
        if search_results:
            if return_book_obj:
                return search_results

            print("\nПо вашему запросу найдены следующие результаты:\n")
            header = f"{'ID':<4} | {'Title':<30} | {'Author':<20} | {'Year':<6} | {'Status':<10}"
            print(header)
            print("-" * len(header))
            
            for book in search_results:
                print(f"{book['id']:<4} | {book['title']:<30} | {book['author']:<20} | {book['year']:<6} | {book['status']:<10}")
        else:
            if return_book_obj:
                return []
            raise NotFoundInTheLibrary("По вашему запросу не было найдено ни одной книги")

    def handle_add_book(self) -> None:
        """Обработка команды добавления книги."""
        while True:
            new_book_data = input(
                "\nВведите название, автора и год издания книги в формате "
                "<название>, <автор>, <год> или -1 для возврата в меню:\n"
            )
            
            if new_book_data == "-1":
                break
            
            try:
                self._add_book(*new_book_data.split(", "))
            except (ValueError, AlreadyInTheLibrary) as exc:
                print(f"\nОшибка: {exc}. Попробуйте снова.")
            except TypeError:
                print("\nОшибка: Параметры добавляемой книги должны быть указаны в формате: "
                      "<название>, <автор>, <год>, а в качестве разделителя должен использоваться ', '")
            else:
                self._update_data(self.library.books_data)
                print("\nКнига успешно добавлена.")
                break

    def handle_delete_book(self) -> None:
        """Обработка команды удаления книги."""
        while True:
            delete_book_id = input("\nВведите ID удаляемой книги или -1 для возврата в меню: ")
            
            if delete_book_id == "-1":
                break

            try:
                delete_book_id = int(delete_book_id)
                self._delete_book(delete_book_id)
            except ValueError:
                print("\nОшибка: Некорректный ввод. ID должен быть целым числом. Попробуйте снова.")
            except NotFoundInTheLibrary as exc:
                print(f"\nОшибка: {exc}. Попробуйте снова.")
            else:
                self._update_data(self.library.books_data)
                print("\nКнига успешно удалена.")
                break

    def handle_change_status(self) -> None:
        """Обработка команды изменения статуса книги."""
        while True:
            book_id = input("\nВведите ID книги для изменения статуса или -1 для возврата в меню: ")
            
            if book_id == "-1":
                break
            
            try:
                book_id = int(book_id)
                self._change_book_status(book_id)
            except ValueError:
                print("\nОшибка: Некорректный ввод. ID должен быть целым числом. Попробуйте снова.")
            except NotFoundInTheLibrary as exc:
                print(f"\nОшибка: {exc}. Попробуйте снова.")
            else:
                self._update_data(self.library.books_data)
                print("\nСтатус книги успешно изменён.")
                break

    def handle_list_books(self) -> None:
        """Обработка команды отображения списка книг."""
        self._list_all_books()

    def handle_search_books(self) -> None:
        """Обработка команды поиска книг."""
        while True:
            search_query = input(
                "\nВведите запрос для поиска книги в формате: <поле> = <значение> или -1 для возврата в меню: "
            )
            
            if search_query == "-1":
                break
            
            try:
                self._search_books_by(search_query)
                break
            except (IncorrectSearchFields, NotFoundInTheLibrary) as exc:
                print(f"\nОшибка: {exc}. Попробуйте снова.")
            except ValueError:
                print("\nОшибка: Поисковый запрос должен быть введен в формате <поле> = <значение>")

    def handle_exit(self) -> None:
        """Обработка команды выхода."""
        print("\nВыход из программы...")

    def run(self) -> None:
        """
        Метод для вызова функции менеджера, соответствующей введённой в консоль команде.
        """
        while True:
            print("\n--- Меню управления библиотекой ---")

            
            for option in MenuOptions:
                print(f"{option.value[0]}. {option.value[1]}")
            
            choice = input("Введите номер команды: ").strip()

            selected_option = None
            for option in MenuOptions:
                if option.value[0] == choice:  # Сравниваем строковое значение с первым элементом кортежа
                    selected_option = option
                    break
            if selected_option is None:
                raise ValueError("\nНекорректный ввод, попробуйте снова.")
            
            match selected_option:
                case MenuOptions.ADD_BOOK:
                    self.handle_add_book()
                case MenuOptions.DELETE_BOOK:
                    self.handle_delete_book()
                case MenuOptions.CHANGE_STATUS:
                    self.handle_change_status()
                case MenuOptions.LIST_BOOKS:
                    self.handle_list_books()
                case MenuOptions.SEARCH_BOOKS:
                    self.handle_search_books()
                case MenuOptions.EXIT:
                    self.handle_exit()
                    break


if __name__ == "__main__":
    manager = LibraryManager()
    manager.run()
    