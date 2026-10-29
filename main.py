"""
Акулинин Андрей Игоревич, Вариант 4

Описание предметной области

Описание хранящихся на складе товаров. Включает в себя: описание помещений, описание стеллажей, 
описание клиентов, описание товаров, хранящихся на стеллажах. Описание помещения состоит из: названия, полезного объёма,
температурных и влажностных условий. Описание стеллажа состоит из: номера, указания помещения,
в котором стеллаж находится, количества мест для хранения в стеллаже, высоты, ширины и длины одного места,
максимальной суммарной нагрузки. Описание клиента состоит из: названия юридического лица и
банковских реквизитов в виде большого текста. Описание товара, хранящегося на стеллажах,
состоит из: высоты, ширины, длины, веса, даты поступления, номера договора, указания, от какого клиента поступил,
даты окончания договора, температурных и влажностных условий хранения, указания стеллажа,
и позиции размещения на нём, представляемой в виде целого номера. На одном стеллаже могут храниться товары разных клиентов.

Таблицы помещения и стеллажи без связей с другими таблицами.
"""
import sys
from datetime import date
from decimal import Decimal, InvalidOperation

sys.path.append("tables")

from final_project_sql_m26_555.project_config import ProjectConfig
from final_project_sql_m26_555.dbconnection import DbConnection
from final_project_sql_m26_555.dbtable import DbTable
from clients_table import ClientsTable
from products_table import ProductsTable


class Main:
    def __init__(self):
        self.config = ProjectConfig()
        self.connection = DbConnection(self.config)
        DbTable.dbconn = self.connection

    def read_next_step(self):
        return input("=> ").strip()

    @staticmethod
    def read_required(prompt, max_length=None):
        while True:
            value = input(prompt).strip()
            if not value:
                print("Значение не может быть пустым.")
                continue
            if max_length and len(value) > max_length:
                print(f"Максимальная длина — {max_length} символов.")
                continue
            return value

    @staticmethod
    def read_positive_decimal(prompt):
        while True:
            try:
                value = Decimal(input(prompt).strip().replace(",", "."))
                if value <= 0:
                    raise InvalidOperation
                return value
            except (InvalidOperation, ValueError):
                print("Введите положительное число.")

    @staticmethod
    def read_decimal(prompt):
        while True:
            value = input(prompt).strip().replace(",", ".")
            if not value:
                print("Поле обязательно. Введите число.")
                continue
            try:
                return Decimal(value)
            except InvalidOperation:
                print("Введите корректное число.")

    @staticmethod
    def read_optional_decimal(prompt):
        while True:
            value = input(prompt).strip().replace(",", ".")
            if not value:
                return None
            try:
                return Decimal(value)
            except InvalidOperation:
                print("Введите число или оставьте поле пустым.")

    @staticmethod
    def read_optional_date(prompt):
        while True:
            value = input(prompt).strip()
            if not value:
                return None
            try:
                return date.fromisoformat(value)
            except ValueError:
                print("Введите дату в формате ГГГГ-ММ-ДД или оставьте поле пустым.")

    def read_yes_no(self, prompt):
        while True:
            answer = input(prompt).strip().lower()

            if answer in ("да", "нет"):
                return answer

            print("Ошибка: введите «да» или «нет».")

    def show_main_menu(self):
        print("""Главное меню:
    1 — клиенты (просмотр, добавление, изменение, удаление)
    9 — выход""")

    def show_clients(self):
        clients = ClientsTable().all()
        print("\nКлиенты:")
        if not clients:
            print("Список пуст.")
        else:
            print("№ | Наименование юрлица")
            for i, c in enumerate(clients, 1):
                print(f"{i} | {c[1]}")
        print("""\nДействия:
    0 — главное меню
    1 — показать товары выбранного клиента
    3 — добавить клиента
    4 — изменить клиента
    5 — удалить клиента
    9 — выход""")
        return self.read_next_step()

    def select_client(self):
        clients = ClientsTable().all()
        if not clients:
            print("Клиентов пока нет.")
            return None
        for i, c in enumerate(clients, 1):
            print(f"{i}. {c[1]}")
        while True:
            raw = input("Выберите номер строки (0 — отмена): ").strip()
            if raw == "0":
                return None
            try:
                pos = int(raw)
                if 1 <= pos <= len(clients):
                    return clients[pos - 1]
            except ValueError:
                pass
            print("Введите номер из списка.")

    def add_client(self):
        name = self.read_required("Наименование юридического лица: ", 200)
        bank = self.read_required("Банковские реквизиты: ")
        try:
            ClientsTable().add(name, bank)
            print("Клиент добавлен.")
        except Exception as exc:
            self.connection.conn.rollback()
            print("Не удалось добавить клиента. Проверьте введённые данные и ограничения БД.")
            print("Подробность:", exc)

    def edit_client(self):
        client = self.select_client()
        if not client:
            return
        print("Оставьте поле пустым, чтобы сохранить прежнее значение.")
        name = input(f"Наименование [{client[1]}]: ").strip() or client[1]
        bank = input(f"Банковские реквизиты [{client[2]}]: ").strip() or client[2]
        if len(name) > 200:
            print("Наименование не должно превышать 200 символов.")
            return
        try:
            ClientsTable().update(client[0], name, bank)
            print("Данные клиента обновлены.")
        except Exception as exc:
            self.connection.conn.rollback()
            print("Не удалось изменить клиента. Проверьте введённые данные и ограничения БД.")
            print("Подробность:", exc)

    def delete_client(self):
        client = self.select_client()
        if not client:
            return
        if ClientsTable().has_products(client[0]):
            print("Нельзя удалить клиента: у него есть товары. Сначала удалите их.")
            return
        if self.read_yes_no(f"Удалить клиента «{client[1]}»? (да/нет): ") == "да":
            try:
                ClientsTable().delete(client[0])
                print("Клиент удалён.")
            except Exception as exc:
                self.connection.conn.rollback()
                print("Не удалось удалить клиента. Возможно, существуют связанные записи.")
                print("Подробность:", exc)

    def show_products(self):
        client = self.select_client()
        if not client:
            return
        products = ProductsTable().all_by_client_id(client[0])
        print(f"\nТовары клиента «{client[1]}»:")
        if not products:
            print("Товаров нет.")
        else:
            print("№ | Стеллаж | Помещение | Размеры (В×Ш×Д) | Вес | Дата | Договор | Поз.")
            for i, p in enumerate(products, 1):
                print(
                    f"{i} | {p[2]} | {p[3]} | "
                    f"{p[4]}×{p[5]}×{p[6]} | {p[7]} | {p[8]} | {p[9]} | {p[15]}"
                )
        print("""\nДействия с товарами:
    0 — назад
    6 — добавить товар этому клиенту
    7 — удалить товар этого клиента""")
        action = self.read_next_step()
        if action == "6":
            self.add_product(client[0])
        elif action == "7":
            self.delete_product(client[0], products)

    def add_product(self, client_id):
        products_table = ProductsTable()
        racks = products_table.racks()
        if not racks:
            print("В таблице rack нет стеллажей. Сначала добавьте стеллаж.")
            return

        print("Стеллажи:")
        for i, r in enumerate(racks, 1):
            print(f"{i}. {r[2]} / стеллаж {r[1]} (мест: {r[3]})")

        while True:
            raw_rack = input("Номер стеллажа из списка (0 — отмена): ").strip()
            if raw_rack == "0":
                return
            try:
                rack_index = int(raw_rack)
                if not 1 <= rack_index <= len(racks):
                    raise ValueError
                rack = racks[rack_index - 1]
                break
            except ValueError:
                print(f"Введите целое число от 1 до {len(racks)} или 0 для отмены.")

        height = self.read_positive_decimal("Высота: ")
        width = self.read_positive_decimal("Ширина: ")
        lengths = self.read_positive_decimal("Длина: ")
        weight = self.read_positive_decimal("Вес: ")
        contract = self.read_required("Номер договора (до 50 символов): ", 50)

        receipt = self.read_optional_date(
            "Дата поступления [пусто = сегодня], ГГГГ-ММ-ДД: "
        )
        if receipt is None:
            receipt = date.today()

        while True:
            end_date = self.read_optional_date("Дата окончания договора (ГГГГ-ММ-ДД): ")
            if end_date is None:
                print("Дата окончания договора обязательна.")
                continue
            if end_date < receipt:
                print("Дата окончания не может быть раньше даты поступления.")
                continue
            break

        while True:
            min_temp = self.read_decimal("Минимальная температура: ")
            max_temp = self.read_decimal("Максимальная температура: ")
            if max_temp > min_temp:
                break
            print("Ошибка: максимальная температура должна быть больше минимальной.")

        while True:
            min_hum = self.read_decimal("Минимальная влажность: ")
            if min_hum < 0:
                print("Ошибка! Минимальная влажность не может быть меньше нуля.")
                continue

            max_hum = self.read_decimal("Максимальная влажность: ")
            if max_hum < 0:
                print("Ошибка! Максимальная влажность не может быть меньше нуля.")
                continue

            if max_hum <= min_hum:
                print(
                    "Ошибка! Максимальная влажность должна быть "
                    "больше минимальной."
                )
                continue

            break

        max_places = rack[3]
        while True:
            raw_position = input(
                f"Номер позиции на стеллаже (1–{max_places}, 0 — отмена): "
            ).strip()
            if raw_position == "0":
                return
            try:
                places = int(raw_position)
                if not 1 <= places <= max_places:
                    print(f"Номер позиции должен быть от 1 до {max_places}.")
                    continue
            except ValueError:
                print("Введите номер позиции целым положительным числом.")
                continue

            if products_table.position_exists(rack[0], places):
                print(
                    f"Позиция №{places} на этом стеллаже уже занята. "
                    "Выберите другой номер."
                )
                continue
            break

        values = [
            rack[0], client_id, height, width, lengths, weight, receipt,
            contract, end_date, min_temp, max_temp, min_hum, max_hum, places
        ]
        try:
            products_table.add_product(values)
            print("Товар успешно добавлен.")
        except Exception as exc:
            self.connection.conn.rollback()
            if products_table.position_exists(rack[0], places):
                print(
                    f"Не удалось добавить товар: позиция №{places} на выбранном "
                    "стеллаже уже занята. Выберите другую позицию."
                )
            else:
                print(
                    "Не удалось добавить товар. Проверьте введённые данные "
                    "и ограничения базы данных."
                )
                print("Подробность:", exc)

    def delete_product(self, client_id, products):
        if not products:
            print("Удалять нечего.")
            return
        raw = input("Введите порядковый номер товара из списка (0 — отмена): ").strip()
        if raw == "0":
            return
        try:
            row_number = int(raw)
            if not 1 <= row_number <= len(products):
                raise ValueError
        except ValueError:
            print("Введите порядковый номер товара из показанного списка.")
            return
        product = products[row_number - 1]
        if self.read_yes_no("Удалить выбранный товар? (да/нет): ") != "да":
            return
        if ProductsTable().delete(product[0], client_id):
            print("Товар удалён.")
        else:
            print("Не удалось найти выбранный товар. Обновите список и повторите.")

    def main_cycle(self):
        while True:
            self.show_main_menu()
            choice = self.read_next_step()
            if choice == "9":
                break
            if choice == "1":
                while True:
                    action = self.show_clients()
                    if action == "0":
                        break
                    if action == "9":
                        self.connection.close()
                        print("До свидания!")
                        return
                    if action == "1":
                        self.show_products()
                    elif action == "3":
                        self.add_client()
                    elif action == "4":
                        self.edit_client()
                    elif action == "5":
                        self.delete_client()
                    else:
                        print("Неизвестный пункт меню.")
            else:
                print("Выберите 1 или 9.")
        self.connection.close()
        print("До свидания!")


if __name__ == "__main__":
    app = Main()
    try:
        app.main_cycle()
    except KeyboardInterrupt:
        print("\nРабота прервана.")
        app.connection.close()
