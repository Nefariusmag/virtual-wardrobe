# virtual-wardrobe

Add ENV in config.py

pip install -r requirements.txt

If we need add new text for babel understand it:
 - in html `{{ _('text') }}`
 - in command line `pybabel extract -F babel.cfg -o messages.pot .` for search new text for translating
 - in command line `pybabel update -i messages.pot -d wardrobe/translations` for update all translation folder
 - add new values in `wardrobe/translations/*/LC_MESSAGES/messages.po` 
 - in command line `pybabel compile -d wardrobe/translations` for generate final version translate 

If we want new leng `pybabel init -i messages.pot -d wardrobe/translations -l ru`

Start flask `__init__.py`, telegram `telega\__init__.py`
