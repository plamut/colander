import unittest

class TestFunctional(unittest.TestCase):
    def _makeSchema(self):
        import cereal

        integer = cereal.Structure(
            'int', cereal.Integer(), validator=cereal.Range(0, 10))
        ob = cereal.Structure('ob', cereal.GlobalObject(package=cereal))

        tup = cereal.Structure('tup', cereal.Tuple())
        tup.add(cereal.Structure('tupint', cereal.Integer()))
        tup.add(cereal.Structure('tupstring', cereal.String()))

        seq = cereal.Structure('seq', cereal.Sequence(tup))

        mapping = cereal.Structure('mapping', cereal.Mapping())
        seq2 = cereal.Structure('seq2', cereal.Sequence(mapping))
        mapping.add(cereal.Structure('key', cereal.Integer()))
        mapping.add(cereal.Structure('key2', cereal.Integer()))

        schema = cereal.Structure('', cereal.Mapping())

        schema.add(integer)
        schema.add(ob)
        schema.add(tup)
        schema.add(seq)
        schema.add(seq2)
        return schema

    def test_deserialize_ok(self):
        import cereal.tests
        data = {
            'int':'10',
            'ob':'cereal.tests',
            'tup':('1', 's'),
            'seq':[('1', 's'),('2', 's'), ('3', 's'), ('4', 's')],
            'seq2':[{'key':'1', 'key2':'2'}, {'key':'3', 'key2':'4'}],
            }
        schema = self._makeSchema()
        result = schema.deserialize(data)
        self.assertEqual(result['int'], 10)
        self.assertEqual(result['ob'], cereal.tests)
        self.assertEqual(result['tup'], (1, 's'))
        self.assertEqual(result['seq'],
                         [(1, 's'), (2, 's'), (3, 's'), (4, 's')])
        self.assertEqual(result['seq2'],
                         [{'key':1, 'key2':2}, {'key':3, 'key2':4}])
        
    def test_invalid_asdict(self):
        expected = {
            'int': '20 is greater than maximum value 10',
            'ob': "The dotted name 'no.way.this.exists' cannot be imported",
            'seq.0.0': "'q' is not a number",
            'seq.1.0': "'w' is not a number",
            'seq.2.0': "'e' is not a number",
            'seq.3.0': "'r' is not a number",
            'seq2.0.key': "'t' is not a number",
            'seq2.0.key2': "'y' is not a number",
            'seq2.1.key': "'u' is not a number",
            'seq2.1.key2': "'i' is not a number",
            'tup.0': "'s' is not a number"}
        import cereal
        data = {
            'int':'20',
            'ob':'no.way.this.exists',
            'tup':('s', 's'),
            'seq':[('q', 's'),('w', 's'), ('e', 's'), ('r', 's')],
            'seq2':[{'key':'t', 'key2':'y'}, {'key':'u', 'key2':'i'}],
            }
        schema = self._makeSchema()
        try:
            schema.deserialize(data)
        except cereal.Invalid, e:
            errors = e.asdict()
            self.assertEqual(errors, expected)