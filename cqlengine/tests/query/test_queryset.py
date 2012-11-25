from cqlengine.tests.base import BaseCassEngTestCase

from cqlengine.exceptions import ModelException
from cqlengine.management import create_column_family
from cqlengine.management import delete_column_family
from cqlengine.models import Model
from cqlengine import columns
from cqlengine import query

class TestModel(Model):
    test_id = columns.Integer(primary_key=True)
    attempt_id = columns.Integer(primary_key=True)
    description = columns.Text()
    expected_result = columns.Integer()
    test_result = columns.Integer()

class IndexedTestModel(Model):
    test_id = columns.Integer(primary_key=True)
    attempt_id = columns.Integer(index=True)
    description = columns.Text()
    expected_result = columns.Integer()
    test_result = columns.Integer(index=True)

class TestQuerySetOperation(BaseCassEngTestCase):

    def test_query_filter_parsing(self):
        """
        Tests the queryset filter method parses it's kwargs properly
        """
        query1 = TestModel.objects(test_id=5)
        assert len(query1._where) == 1

        op = query1._where[0]
        assert isinstance(op, query.EqualsOperator)
        assert op.value == 5

        query2 = query1.filter(expected_result__gte=1)
        assert len(query2._where) == 2

        op = query2._where[1]
        assert isinstance(op, query.GreaterThanOrEqualOperator)
        assert op.value == 1

    def test_using_invalid_column_names_in_filter_kwargs_raises_error(self):
        """
        Tests that using invalid or nonexistant column names for filter args raises an error
        """
        with self.assertRaises(query.QueryException):
            query0 = TestModel.objects(nonsense=5)

    def test_where_clause_generation(self):
        """
        Tests the where clause creation
        """
        query1 = TestModel.objects(test_id=5)
        ids = [o.identifier for o in query1._where]
        where = query1._where_clause()
        assert where == 'test_id = :{}'.format(*ids)

        query2 = query1.filter(expected_result__gte=1)
        ids = [o.identifier for o in query2._where]
        where = query2._where_clause()
        assert where == 'test_id = :{} AND expected_result >= :{}'.format(*ids)


    def test_querystring_generation(self):
        """
        Tests the select querystring creation
        """

    def test_queryset_is_immutable(self):
        """
        Tests that calling a queryset function that changes it's state returns a new queryset
        """
        query1 = TestModel.objects(test_id=5)
        assert len(query1._where) == 1

        query2 = query1.filter(expected_result__gte=1)
        assert len(query2._where) == 2

    def test_the_all_method_clears_where_filter(self):
        """
        Tests that calling all on a queryset with previously defined filters returns a queryset with no filters
        """
        query1 = TestModel.objects(test_id=5)
        assert len(query1._where) == 1

        query2 = query1.filter(expected_result__gte=1)
        assert len(query2._where) == 2

        query3 = query2.all()
        assert len(query3._where) == 0

    def test_defining_only_and_defer_fails(self):
        """
        Tests that trying to add fields to either only or defer, or doing so more than once fails
        """

    def test_defining_only_or_defer_on_nonexistant_fields_fails(self):
        """
        Tests that setting only or defer fields that don't exist raises an exception
        """

class BaseQuerySetUsage(BaseCassEngTestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseQuerySetUsage, cls).setUpClass()
        delete_column_family(TestModel)
        delete_column_family(IndexedTestModel)
        create_column_family(TestModel)
        create_column_family(IndexedTestModel)

        TestModel.objects.create(test_id=0, attempt_id=0, description='try1', expected_result=5, test_result=30)
        TestModel.objects.create(test_id=0, attempt_id=1, description='try2', expected_result=10, test_result=30)
        TestModel.objects.create(test_id=0, attempt_id=2, description='try3', expected_result=15, test_result=30)
        TestModel.objects.create(test_id=0, attempt_id=3, description='try4', expected_result=20, test_result=25)

        TestModel.objects.create(test_id=1, attempt_id=0, description='try5', expected_result=5, test_result=25)
        TestModel.objects.create(test_id=1, attempt_id=1, description='try6', expected_result=10, test_result=25)
        TestModel.objects.create(test_id=1, attempt_id=2, description='try7', expected_result=15, test_result=25)
        TestModel.objects.create(test_id=1, attempt_id=3, description='try8', expected_result=20, test_result=20)

        TestModel.objects.create(test_id=2, attempt_id=0, description='try9', expected_result=50, test_result=40)
        TestModel.objects.create(test_id=2, attempt_id=1, description='try10', expected_result=60, test_result=40)
        TestModel.objects.create(test_id=2, attempt_id=2, description='try11', expected_result=70, test_result=45)
        TestModel.objects.create(test_id=2, attempt_id=3, description='try12', expected_result=75, test_result=45)

        IndexedTestModel.objects.create(test_id=0, attempt_id=0, description='try1', expected_result=5, test_result=30)
        IndexedTestModel.objects.create(test_id=1, attempt_id=1, description='try2', expected_result=10, test_result=30)
        IndexedTestModel.objects.create(test_id=2, attempt_id=2, description='try3', expected_result=15, test_result=30)
        IndexedTestModel.objects.create(test_id=3, attempt_id=3, description='try4', expected_result=20, test_result=25)

        IndexedTestModel.objects.create(test_id=4, attempt_id=0, description='try5', expected_result=5, test_result=25)
        IndexedTestModel.objects.create(test_id=5, attempt_id=1, description='try6', expected_result=10, test_result=25)
        IndexedTestModel.objects.create(test_id=6, attempt_id=2, description='try7', expected_result=15, test_result=25)
        IndexedTestModel.objects.create(test_id=7, attempt_id=3, description='try8', expected_result=20, test_result=20)

        IndexedTestModel.objects.create(test_id=8, attempt_id=0, description='try9', expected_result=50, test_result=40)
        IndexedTestModel.objects.create(test_id=9, attempt_id=1, description='try10', expected_result=60, test_result=40)
        IndexedTestModel.objects.create(test_id=10, attempt_id=2, description='try11', expected_result=70, test_result=45)
        IndexedTestModel.objects.create(test_id=11, attempt_id=3, description='try12', expected_result=75, test_result=45)

    @classmethod
    def tearDownClass(cls):
        super(BaseQuerySetUsage, cls).tearDownClass()
        delete_column_family(TestModel)
        delete_column_family(IndexedTestModel)

class TestQuerySetCountAndSelection(BaseQuerySetUsage):

    def test_count(self):
        assert TestModel.objects.count() == 12

        q = TestModel.objects(test_id=0)
        assert q.count() == 4

    def test_iteration(self):
        q = TestModel.objects(test_id=0)
        #tuple of expected attempt_id, expected_result values
        compare_set = set([(0,5), (1,10), (2,15), (3,20)])
        for t in q:
            val = t.attempt_id, t.expected_result
            assert val in compare_set
            compare_set.remove(val)
        assert len(compare_set) == 0

        q = TestModel.objects(attempt_id=3)
        assert len(q) == 3
        #tuple of expected test_id, expected_result values
        compare_set = set([(0,20), (1,20), (2,75)])
        for t in q:
            val = t.test_id, t.expected_result
            assert val in compare_set
            compare_set.remove(val)
        assert len(compare_set) == 0
        
    def test_delete(self):
        TestModel.objects.create(test_id=3, attempt_id=0, description='try9', expected_result=50, test_result=40)
        TestModel.objects.create(test_id=3, attempt_id=1, description='try10', expected_result=60, test_result=40)
        TestModel.objects.create(test_id=3, attempt_id=2, description='try11', expected_result=70, test_result=45)
        TestModel.objects.create(test_id=3, attempt_id=3, description='try12', expected_result=75, test_result=45)
        
        assert TestModel.objects.count() == 16
        assert TestModel.objects(test_id=3).count() == 4
        
        TestModel.objects(test_id=3).delete()
        
        assert TestModel.objects.count() == 12
        assert TestModel.objects(test_id=3).count() == 0

class TestQuerySetIterator(BaseQuerySetUsage):

    def test_multiple_iterations_work_properly(self):
        """ Tests that iterating over a query set more than once works """
        q = TestModel.objects(test_id=0)
        #tuple of expected attempt_id, expected_result values
        compare_set = set([(0,5), (1,10), (2,15), (3,20)])
        for t in q:
            val = t.attempt_id, t.expected_result
            assert val in compare_set
            compare_set.remove(val)
        assert len(compare_set) == 0

        #try it again
        compare_set = set([(0,5), (1,10), (2,15), (3,20)])
        for t in q:
            val = t.attempt_id, t.expected_result
            assert val in compare_set
            compare_set.remove(val)
        assert len(compare_set) == 0

class TestQuerySetOrdering(BaseQuerySetUsage):

    def test_order_by_success_case(self):

        q = TestModel.objects(test_id=0).order_by('attempt_id')
        expected_order = [0,1,2,3]
        for model, expect in zip(q,expected_order):
            assert model.attempt_id == expect

        q = q.order_by('-attempt_id')
        expected_order.reverse()
        for model, expect in zip(q,expected_order):
            assert model.attempt_id == expect

    def test_ordering_by_non_second_primary_keys_fail(self):

        with self.assertRaises(query.QueryException):
            q = TestModel.objects(test_id=0).order_by('test_id')

    def test_ordering_by_non_primary_keys_fails(self):
        with self.assertRaises(query.QueryException):
            q = TestModel.objects(test_id=0).order_by('description')

    def test_ordering_on_indexed_columns_fails(self):
        with self.assertRaises(query.QueryException):
            q = IndexedTestModel.objects(test_id=0).order_by('attempt_id')

class TestQuerySetSlicing(BaseQuerySetUsage):
    pass

class TestQuerySetValidation(BaseQuerySetUsage):

    def test_primary_key_or_index_must_be_specified(self):
        """
        Tests that queries that don't have an equals relation to a primary key or indexed field fail
        """
        with self.assertRaises(query.QueryException):
            q = TestModel.objects(test_result=25)
            iter(q)

    def test_primary_key_or_index_must_have_equal_relation_filter(self):
        """
        Tests that queries that don't have non equal (>,<, etc) relation to a primary key or indexed field fail
        """
        with self.assertRaises(query.QueryException):
            q = TestModel.objects(test_id__gt=0)
            iter(q)


    def test_indexed_field_can_be_queried(self):
        """
        Tests that queries on an indexed field will work without any primary key relations specified
        """
        q = IndexedTestModel.objects(test_result=25)
        count = q.count()
        assert q.count() == 4










