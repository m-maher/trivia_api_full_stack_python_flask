import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

database_path = 'postgresql://postgres:postgres@localhost:5432/trivia'


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = database_path
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test
    for successful operation and for expected errors.
    """

# General Test

    def test_endpoint_not_available(self):
        """Test getting an endpoint which does not exist """
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        # self.assertEqual(data['message'], 'resource not found')

# Tests for /categories/<string:category_id>/questions GET

    def test_get_questions_from_category(self):
        """Test GET all questions from selected category."""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], '1')

    def test_400_get_questions_from_category(self):
        """Test 400 if no questions with queried category is available."""
        res = self.client().get('/categories/1212/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        # self.assertEqual(data['message'], False)

# Tests for /questions POST

    def test_create_question(self):
        """Test POST a new question """

        # Used as header to POST /question
        json_create_question = {
            'question': 'Is this a test question?',
            'answer': 'Yes it is!',
            'category': '1',
            'difficulty': 1
        }

        res = self.client().post('/questions', json=json_create_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'] > 0)

    def test_error_create_question(self):
        """Test POST a new question with missing category """

        # Used as header to POST /question
        json_create_question_error = {
            'question': 'Is this a test question?',
            'answer': 'Yes it is!',
            'difficulty': 1
        }

        res = self.client().post('/questions', json=json_create_question_error)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        # self.assertEqual(data['message'], 'Category can not be blank')

    def test_search_question(self):
        """Test POST to search a question with an existing search term. """

        # Used as header to POST /question
        json_search_question = {
            'searchTerm': 'test',
        }

        res = self.client().post('/questions', json=json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_error_404_search_question(self):
        """Test POST to search a question with non existing search term. """

        json_search_question = {
            'searchTerm': 'there is no question with such a string in it',
        }

        res = self.client().post('/questions', json=json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

# # Tests for /categories GET

    def test_get_all_categories(self):
        """Test GET all categories. """
        json_create_category = {
            'type': 'Adult Stuff'
        }

        res = self.client().post('/categories', json=json_create_category)

        res = self.client().get('/categories')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']) > 0)

# # Tests for /questions GET

    def test_get_all_questions_paginated(self):
        """Test GET all questions from all categories.
        JSON body should not have any impact. """
        res = self.client().get('/questions?page=1',
                                json={'category:': 'science'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'] > 0)

# # BONUS: Tests for /categories DELETE

    def test_delete_category(self):
        """Test DELETE /categories """

        last_category_id = Category.query.order_by(Category.id).first().id
        res = self.client().delete('/categories/{}'.format(last_category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_404_delete_category(self):
        """Test error DELETE /categories with an id which does not exist """
        res = self.client().delete('/categories/{}'.format(1234567879))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

# # Tests for /questions DELETE

    def test_delete_question(self):
        """Test DELETE /question """

        json_create_question = {
            'question': 'Will this question last long?',
            'answer': 'No, it will be deleted soon!',
            'category': '1',
            'difficulty': 1
        }

        res = self.client().post('/questions', json=json_create_question)
        data = json.loads(res.data)
        question_id = data['created']

        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_id)

    def test_404_delete_question(self):
        """Test error DELETE /question with an id which does not exist """
        res = self.client().delete('/questions/{}'.format(1234567879))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

# # Tests for /quizzes POST

    def test_play_quiz_with_category(self):
        """Test /quizzes succesfully with given category """
        json_play_quizz = {
            'previous_questions': [1, 2, 5],
            'quiz_category': {
                'type': 'Science',
                'id': '1'
            }
        }
        res = self.client().post('/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['id']
                        not in json_play_quizz['previous_questions'])

    def test_play_quiz_game(self):
        """Tests playing quiz game success"""

        response = self.client().post('/quizzes',
                                      json={'previous_questions': [20, 21],
                                            'quiz_category': {
                                                'type': 'Science', 'id': '1'
                                      }
                                      })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 20)
        self.assertNotEqual(data['question']['id'], 21)

    def test_play_quiz_fails(self):
        """Tests playing quiz game failure 400"""

        response = self.client().post('/quizzes', json={})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
