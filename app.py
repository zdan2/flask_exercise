from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# --- Flaskアプリの初期化 ---
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app

app = create_app()
db = SQLAlchemy(app)

# --- モデル定義 ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.before_request
def create_tables():
    db.create_all()
# --- ルーティング定義 ---

@app.route('/')
def index():
    """
    商品一覧を表示するルート。
    ?sort_by=<列名>&order=<asc|desc> でソート順を指定できる。
    例： /?sort_by=price&order=desc
    """
    # クエリパラメータ取得
    sort_by = request.args.get('sort_by', 'id')  # デフォルトは id
    order = request.args.get('order', 'asc')     # デフォルトは asc

    # sort_by が想定外の値なら id へフォールバック
    if sort_by not in ['id', 'name', 'price']:
        sort_by = 'id'

    # データの取得
    query = Product.query
    if order == 'desc':
        query = query.order_by(db.desc(getattr(Product, sort_by)))
    else:
        query = query.order_by(getattr(Product, sort_by))

    products = query.all()
    return render_template('index.html', products=products, sort_by=sort_by, order=order)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    """
    商品を追加するためのルート。
    GETの場合はフォームを表示し、POSTの場合にDBへ登録する。
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()

        # --- 入力値チェック ---
        # 商品名未入力
        if not name:
            error = "商品名を入力してください。"
            return render_template('add_product.html', error=error)

        # 価格が数値として解釈できるか、かつ正の値か
        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            error = "価格には0以上の数値を入力してください。"
            return render_template('add_product.html', error=error)

        # --- DBに登録 ---
        product = Product(name=name, price=price)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('index'))

    # GETの場合のフォーム表示
    return render_template('add_product.html')

# --- メイン実行部 ---
if __name__ == '__main__':
    # 初回起動時などにテーブルを作成する
    with app.app_context():
        db.create_all()

    # デバッグモードで起動
    app.run(debug=True)
