# virtual-wardrobe

Create DataBase on Postgres (ver.9.6)

Add ENV in database.py

pip install -r requirements.txt

If we need add new text for babel understand it:
 - in html `{{ _('text') }}`
 - in comand line `pybabel extract -F babel.cfg -o messages.pot .`
 - in comand line `pybabel update -i messages.pot -d wardrobe/translations`
 - in comand line `pybabel compile -d wardrobe/translations`

If we want new leng `pybabel init -i messages.pot -d wardrobe/translations -l ru`
