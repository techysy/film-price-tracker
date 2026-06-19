from models.film import session, Film, PriceHistory

# 检查胶卷数据
print("检查胶卷数据...")
films = session.query(Film).all()
print(f"胶卷数量: {len(films)}")

for film in films:
    print(f"胶卷: {film.brand} {film.model}")
    # 检查价格历史
    price_histories = session.query(PriceHistory).filter_by(film_id=film.id).all()
    print(f"  价格历史记录数: {len(price_histories)}")

# 如果没有胶卷数据，添加一些示例数据
if len(films) == 0:
    print("\n添加示例数据...")
    
    # 添加柯达 Gold 200
    film1 = Film(
        brand="柯达",
        model="Gold 200",
        iso=200,
        format="35mm",
        description="柯达 Gold 200 彩色负片"
    )
    session.add(film1)
    
    # 添加富士 Superia X-Tra 400
    film2 = Film(
        brand="富士",
        model="Superia X-Tra 400",
        iso=400,
        format="35mm",
        description="富士 Superia X-Tra 400 彩色负片"
    )
    session.add(film2)
    
    # 提交数据
    session.commit()
    print("示例数据添加完成！")
