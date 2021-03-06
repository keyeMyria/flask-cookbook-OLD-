from cookbook.models import Recipe, Step, Note, Ingredient, Department, Unit, RecipeIngredient
from cookbook.schemas import DepartmentSchema, IngredientSchema, UnitSchema, StepSchema
from cookbook.schemas import NoteSchema, RecipeSchema
from flask_testing import TestCase
from cookbook import db, app
from flask_fixtures import FixturesMixin
import json
import pprint
import unittest 
import csv
import requests

FixturesMixin.init_app(app, db)


class TestClient(object):
    def post(self, url, json_data):
        url = 'http://127.0.0.1:5000' + url
        json_data = json.loads(json_data)
        return requests.post(url, json=json_data)
        #return app.test_client().post(url, data=json_data,
        #               content_type = 'application/json')

    def put(self, url, json_data):
        url = 'http://127.0.0.1:5000' + url
        json_data = json.loads(json_data)
        return requests.put(url, json=json_data)
        #return app.test_client().put(url, data=json_data,
        #               content_type = 'application/json')
    
    def delete(self, url):
        url = 'http://127.0.0.1:5000' + url
        return requests.delete(url)
        #return app.test_client().delete(url)
    
    def get(self, url):
        url = 'http://127.0.0.1:5000' + url
        return requests.get(url)
        #return app.test_client().get(url)
        
    
       
class ViewTest(TestCase, FixturesMixin):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    fixtures = ['recipes.json',
                'steps.json',
                'notes.json',
                'units.json',
                'ingredients.json',
                'departments.json',
                'recipeingredients.json']
    
    __test__ = False
    
    def create_app(self):
        app.config.from_object('config.TestingConfig')
        #app.config.from_object('config.TestingLocalDBConfig')
        return app
    @unittest.skip('skipping') 
    def test_get_one(self):
        app.logger.debug('starting test_get_one Model = {}'.format(repr(self)))
        url_endpoint = self.url_base + str(self.test_data['id'])
        app.logger.debug('Getting URL: {}'.format(url_endpoint))
        result = TestClient().get(url_endpoint)
        app.logger.debug('GET result:  {}'.format(result.content))
        assert result.status_code == 200
        data, errors = self.schema().loads(result.content)
        assert errors == {}
        assert isinstance(data, self.component) == True
        assert data.name == self.test_data['name']
        assert data.id == self.test_data['id']
    @unittest.skip('skipping')  
    def test_get_not_existing(self):
        url_endpoint = self.url_base + str(self.test_data['bad_id'])
        result = app.test_client().get(url_endpoint)
        assert result.status_code == 404
        assert isinstance(result.data, str) 
    def test_get_all(self):
        url_endpoint = self.url_base
        result = TestClient().get(url_endpoint)
        assert result.status_code == 200
        data, errors = self.schema(many=True).loads(result.content)
        assert len(data) == self.test_data['total_num']
        assert data[0].name == self.test_data['name']
    @unittest.skip('skipping')
    def test_create_item(self):
        app.logger.debug('Starting create_item test for {}'.format(repr(self)))
        app.logger.debug('Existing Departments:  {}')
        url_endpoint = self.url_base
        result = TestClient().post(url_endpoint, self.new_item_string)
        assert result.status_code == 200
        app.logger.debug('Post result = {}'.format(result.content))
        result = TestClient().get(url_endpoint)
        assert result.status_code == 200
        assert self.test_data['new_item'] in result.contents
        
    @unittest.skip('skipping')     
    def test_delete_item(self):
        url_endpoint = self.url_base + str(self.test_data['id'])
        result = TestClient().delete(url_endpoint)
        assert result.status_code == 200
        result = TestClient().get(url_endpoint)
        assert result.status_code == 404
    @unittest.skip('skipping')  
    def test_update_item(self):
        url_endpoint = self.url_base + str(self.test_data['id'])
        result = TestClient().put(url_endpoint, self.update_item_string)
        assert self.component.query.get(1).name == self.test_data['updated_item']
@unittest.skip('skipping')   
class IngredientsViewTest(ViewTest):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        ViewTest.__init__(self, *args, **kwargs)
        self.url_base = '/ingredients/'
        self.test_data = {'id' : 1,
                          'bad_id' : 15,
                          'name' : 'cauliflower', 
                          'department' : 1,
                          'total_num' : 5,
                          'new_item' : 'ground pork',
                          'updated_item' : 'watermelon'}
        self.component = Ingredient
        self.schema = IngredientSchema   
        self.new_item_string = r"""{"name" : "ground pork", "department" : { "id" : 2, "name" : "Meat"}}"""
        self.update_item_string = r"""{"name" : "watermelon"}"""
    
    def test_create_ingredient_missing_department(self):
        ing = r"""{"name" : "ground pork"}"""
        result = TestClient().post('/ingredients/', ing)
        assert 'Missing data' in result.data
    
    def test_update_ingredient_department(self):
        assert Ingredient.query.get(1).name == 'cauliflower'
        ing = r"""{"department" : {"name" : "Meat", "id" : 3}}"""
        result = TestClient().put('/ingredients/1', ing)
        assert result.status_code == 200
        assert Ingredient.query.get(1).name == 'cauliflower'
        assert Ingredient.query.get(1).department.id == 3
        assert Department.query.get(3).name == 'Meat'

        
class DepartmentsViewTest(ViewTest):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        ViewTest.__init__(self, *args, **kwargs)
        self.url_base = '/departments/'
        self.test_data = {'id' : 1,
                          'bad_id' : 15,
                          'name' : 'Produce', 
                          'total_num' : 4,
                          'new_item' : 'hba',
                          'updated_item' : 'floral'}
        self.component = Department
        self.schema = DepartmentSchema   
        self.new_item_string = r"""{"name" : "hba"}"""
        self.update_item_string = r"""{"name" : "floral"}"""
        
    def test_query_arg(self):
        result = TestClient().get('/departments/?q=asdf&somedata=zxcv&sort=jkll')

@unittest.skip('skipping')        
class UnitsViewTest(ViewTest):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        ViewTest.__init__(self, *args, **kwargs)
        self.url_base = '/units/'
        self.test_data = {'id' : 1,
                          'bad_id' : 15,
                          'name' : 'tablespoon', 
                          'total_num' : 4,
                          'new_item' : 'pound',
                          'updated_item' : 'liter'}
        self.component = Unit
        self.schema = UnitSchema
        self.new_item_string = r"""{"name" : "pound"}"""
        self.update_item_string = r"""{"name" : "liter"}"""
@unittest.skip('skipping')     
class RecipesViewTest(ViewTest):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        ViewTest.__init__(self, *args, **kwargs)
        self.url_base = '/recipes/'
        self.test_data = {'id' : 1,
                          'bad_id' : 15,
                          'name' : 'Spaghetti and Meatballs', 
                          'total_num' : 3,
                          'new_item' : 'Burrito',
                          'updated_item' : 'Lasagna'}
        self.component = Recipe
        self.schema = RecipeSchema
        self.new_item_string = r"""{"name" : "Burrito", "rating" : 5, 
                                    "steps" : [{"order" : 1, "step" : "brown beef"},
                                                {"order" : 2, "step" : "add seasoning"},
                                                {"order" : 3, "step" : "cook unitl done"}],
                                    "notes" : [{"note" : "use old el paso"}]}"""
        self.update_item_string = r"""{"name" : "Lasagna"}"""   

    def test_all_new(self):
        #new recipe
        json_string = r"""{"name": "Meatloaf", "steps" : [{"step" : "Combine meat, seasonings", "order" : 1},
                          {"step" : "Shape into loaf pan", "order" : 2}, {"step" : "Bake for 1 hour", "order" : 3}], 
                           "notes" : [{"note" : "Dont forget the liver"}, {"note" : "and fish sauce"}], "rating" : 5}"""
        result = TestClient().post('/recipes/', json_string)
        assert result.status_code == 200
        new_rec = Recipe.query.get(4)
        assert new_rec.id == 4
        assert new_rec.name == 'Meatloaf'
        assert len(new_rec.steps.all()) == 3
        assert len(new_rec.notes.all()) == 2
        assert new_rec.steps[0].step == "Combine meat, seasonings"
@unittest.skip('skipping')        
class RequestsViewTest(ViewTest):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        ViewTest.__init__(self, *args, **kwargs)
        self.component = Ingredient
        self.schema = IngredientSchema
    
    def test_request_post(self):
        with open('ingredients.csv', 'rb') as csvfile:
            ingredients = csv.reader(csvfile, delimiter=',')
            for ingred, depart in ingredients:
                print 'ingred: {}    department:  {}'.format(ingred.lower(), depart.lower())
                ingred = ingred.lower()
                depart = depart.lower()
                payload = {'name' : ingred, 'department' : {'name' : depart}}
                #payload = r"""{"name" : "ground lamb", "department" : { "id" : 2, "name" : "Meat"}}"""
                #payload = json.dumps(payload)
                r = requests.post('http://127.0.0.1:5000/ingredients/', json=payload)
                print r.status_code
                print r.content


    def test_get_one(self):
        pass

    def test_get_not_existing(self):
        pass
    
    def test_get_all(self):
        pass
        
    def test_create_item(self):
        pass
        
    def test_delete_item(self):
        pass

    def test_update_item(self):
        pass