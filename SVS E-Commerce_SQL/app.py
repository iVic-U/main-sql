# app.py
from typing import Optional, Any, Dict, List
from passlib.hash import bcrypt
from db import fetch_one, fetch_all, execute, get_db_connection, DatabaseError
import sqlite3

current_user: Optional[dict[str,Any]] = None  # usuario logueado

# ---------- Helpers ----------

def input_nonempty(prompt: str) -> str:
    while True:
        v = input(prompt).strip()
        if v:
            return v

def row_to_dict(row: sqlite3.Row | None) -> Dict[str, Any] | None:
    """Convierte sqlite3.Row a dict o devuelve None."""
    if row is None:
        return None
    return dict(row)

# ---------- Registro/Login ----------

def register() -> None:
    print("\n== Registro ==")
    first = input_nonempty("Nombre: ")
    last = input_nonempty("Apellido: ")
    email = input_nonempty("Email: ")
    phone = input("Teléfono (opcional): ").strip()
    address = input_nonempty("Dirección: ")
    pwd = input_nonempty("Contraseña: ")
    ph = bcrypt.hash(pwd)

    try:
        execute(
            "INSERT INTO users (first_name, last_name, email, phone, address, password_hash) VALUES (?, ?, ?, ?, ?, ?)",
            (first, last, email, phone, address, ph)
        )
        # crear carrito
        user = fetch_one("SELECT id FROM users WHERE email = ?", (email,))
        if user:
            execute("INSERT INTO carts (user_id) VALUES (?)", (user["id"],))
        print("Registro exitoso.")
    except Exception as e:
        print("Error al registrar:", e)

def login() -> None:
    global current_user
    print("\n== Login ==")
    identifier = input_nonempty("Email o teléfono: ")
    pwd = input_nonempty("Contraseña: ")
    user = fetch_one("SELECT * FROM users WHERE email = ? OR phone = ?", (identifier, identifier))
    if user and bcrypt.verify(pwd, user["password_hash"]):
        current_user = dict(user)
        print(f"Bienvenido {user['first_name']} ({user['role']})")
    else:
        print("Credenciales inválidas.")

def logout() -> None:
    global current_user
    current_user = None
    print("Sesión cerrada.")

# ---------- Productos ----------

def list_products() -> None:
    rows = fetch_all("SELECT * FROM products")
    if not rows:
        print("No hay productos.")
        return
    print("\n== Productos ==")
    for r in rows:
        price = r["price"]
        if r["discount_percent"]:
            price *= (1 - r["discount_percent"]/100)
        print(f"{r['id']}: {r['name']} - ${price:.2f} | Stock: {r['stock']}")

# ---------- Carrito ----------

def add_to_cart() -> None:
    if not current_user or current_user["role"] != "user":
        print("Debes iniciar sesión como usuario.")
        return
    pid = input_nonempty("ID producto: ")
    qty = int(input_nonempty("Cantidad: "))
    prod = fetch_one("SELECT * FROM products WHERE id = ?", (pid,))
    if not prod:
        print("Producto no existe.")
        return
    cart = fetch_one("SELECT id FROM carts WHERE user_id = ?", (current_user["id"],))
    if not cart:
        cid = execute("INSERT INTO carts (user_id) VALUES (?)", (current_user["id"],))
        cart_id = cid
    else:
        cart_id = cart["id"]
    execute("INSERT INTO cart_items (cart_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (cart_id, pid, qty, prod["price"]))
    print("Producto añadido al carrito.")

def view_cart() -> None:
    if not current_user:
        print("Inicia sesión.")
        return
    cart = fetch_one("SELECT id FROM carts WHERE user_id = ?", (current_user["id"],))
    if not cart:
        print("Carrito vacío.")
        return
    items = fetch_all("SELECT ci.id, p.name, ci.quantity, ci.unit_price FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.cart_id = ?", (cart["id"],))
    if not items:
        print("Carrito vacío.")
        return
    total = sum(it["quantity"] * it["unit_price"] for it in items)
    print("\n== Carrito ==")
    for it in items:
        print(f"{it['name']} x{it['quantity']} @ ${it['unit_price']:.2f}")
    print(f"Total: ${total:.2f}")

# --- checkout_transactional(user_id: int) ---


def checkout_transactional(user_id: int, address: str) -> int:
    """
    Crea una orden para el carrito del user_id.
    Devuelve order_id si OK, lanza sqlite3.Error o DatabaseError en fallo.
    """
    # obtener cart id y items
    cart_row = fetch_one("SELECT id FROM carts WHERE user_id = ?", (user_id,))
    if not cart_row:
        raise ValueError("Carrito vacío")
    cart_id = int(cart_row["id"])

    items = fetch_all(
        "SELECT ci.product_id, p.name, ci.quantity, ci.unit_price, p.stock "
        "FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.cart_id = ?",
        (cart_id,)
    )
    if not items:
        raise ValueError("Carrito vacío")

    # validar stock y calcular total
    total = 0.0
    for it in items:
        qty = int(it["quantity"])
        stock = int(it["stock"])
        if qty > stock:
            raise ValueError(f"Stock insuficiente para {it['name']}")
        total += qty * float(it["unit_price"])

    # transacción atómica
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (user_id, status, total_amount, address) VALUES (?, 'pending', ?, ?)",
            (user_id, total, address)
        )
        order_id = cur.lastrowid
        if order_id is None:
            raise ValueError("Failed to insert order")
        for it in items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, it["product_id"], it["quantity"], it["unit_price"])
            )
            cur.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (it["quantity"], it["product_id"])
            )
        cur.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
    return order_id

# ---------- Admin ----------
def admin_menu() -> None:
    while True:
        print("\n== Admin Menu ==")
        print("1) Crear producto")
        print("2) Ver productos")
        print("0) Volver")
        opt = input("Opción: ").strip()
        if opt == "1":
            name = input_nonempty("Nombre: ")
            desc = input("Descripción: ")
            price = float(input_nonempty("Precio: "))
            stock = int(input_nonempty("Stock: "))
            execute("INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
                    (name, desc, price, stock))
            print("Producto creado.")
        elif opt == "2":
            list_products()
        elif opt == "0":
            break

# --- view_orders_for_user(user_id: int) ---
def view_orders_for_user(user_id: int) -> List[Dict[str, Any]]:
    """Devuelve lista de órdenes con items para un usuario."""
    orders = fetch_all("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    result: List[Dict[str, Any]] = []
    for o in orders:
        try:
            items = fetch_all(
            "SELECT oi.quantity, oi.unit_price, p.name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
            (o["id"],)
            )
        except DatabaseError:
            items = []
        result.append({"order": dict(o), "items": [dict(it) for it in items]})
    return result

# ---------- Menús ----------
def guest_menu() -> None:
    while True:
        print("\n== Menú invitado ==")
        print("1) Ver productos")
        print("2) Registrarse")
        print("3) Iniciar sesión")
        print("0) Salir")
        opt = input("Opción: ").strip()
        if opt == "1":
            list_products()
        elif opt == "2":
            register()
        elif opt == "3":
            login()
            if current_user:
                if current_user["role"] == "admin":
                    admin_menu()
                else:
                    user_menu()
        elif opt == "0":
            break

def user_menu() -> None:
    while current_user:
        print("\n== Menú usuario ==")
        print("1) Ver productos")
        print("2) Añadir al carrito")
        print("3) Ver carrito")
        print("4) Cerrar sesión")
        opt = input("Opción: ").strip()
        if opt == "1":
            list_products()
        elif opt == "2":
            add_to_cart()
        elif opt == "3":
            view_cart()
        elif opt == "4":
            logout()
            break
        elif opt == "5":  # Checkout
            try:
                order_id = checkout_transactional(int(current_user["id"]), current_user.get("address", ""))
                print(f"Compra realizada. ID orden: {order_id}")
            except ValueError as ve:
                print("No se pudo completar la compra:", ve)
            except DatabaseError as de:
                print("Error en la base de datos:", de)
        elif opt == "6":
            try:
                orders = view_orders_for_user(int(current_user["id"]))
                if not orders:
                    print("No tienes órdenes.")
                for o in orders:
                    ord_info = o["order"]
                    print(f"Orden {ord_info['id']} | ${ord_info['total_amount']:.2f} | {ord_info['status']} | {ord_info['created_at']}")
                    for it in o["items"]:
                        print(f"  - {it['name']} x{it['quantity']} @ ${it['unit_price']:.2f}")
            except DatabaseError as de:
                print("Error al obtener órdenes:", de)


def main() -> None:
    print("=== ECOMMERCE CONSOLA ===")
    while True:
        if not current_user:
            guest_menu()
        else:
            if current_user["role"] == "admin":
                admin_menu()
            else:
                user_menu()

if __name__ == "__main__":
    main()
