from __future__ import (
    unicode_literals
)
from copy import deepcopy
import os
import yaml


class Config(object):
    @staticmethod
    def load(name='bifrost.cfg'):
        with(open(name)) as fp:
            return yaml.load(fp.read())

    @staticmethod
    def load_from_template():
        tmpl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                '../_templates/config-yaml.tpl')

        with(open(tmpl_path)) as fp:
            return yaml.load(fp.read())

    @staticmethod
    def save(name='bifrost.cfg', connection={}, deployment={},
                                    repository=None, roles={}, **kwargs):
        tmpl_data = deepcopy(Config.load_from_template())

        tmpl_data['connection'].update(connection)
        tmpl_data['deployment'].update(deployment)

        with(open(name, 'w')) as fp:
            fp.write(yaml.dump(tmpl_data))

    @staticmethod
    def _get_file_path():
        return os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            '_templates/config-yaml.tpl')


class ConfigBuilder(object):
    def __init__(self, key, data):
        self.values = {}
        self.key = key

        self._questions = {}
        if isinstance(data, basestring):
            data = {key: data}

        for k, v in data.iteritems():
            self._questions[k] = {
                'key': k,
                'default': v,
                'required': True,
                'is_array': isinstance(v, list)
            }

    def change_question(self, question, **kwargs):
        q = self._questions[question]
        q.update(kwargs)

    def prompt_user(self):
        print 'Please answer the following questions relating to {}...'.format(self.key)
        for key, question in self._questions.iteritems():
            if question.get('skip'):
                self.values[key] = question['default']
            else:
                self.values[key] = self._get_answer_for_question(question)

        return self.values

    def _get_answer_for_question(self, question, indent=2):
        question_string = '{indent}{component} [default: {default}, type: {type}]: '.format(
            indent=' '*indent,
            component=question['key'],
            default=question['default'],
            type='string' if not question['is_array'] else 'list - seperate by comma'
         )
        answer = raw_input(question_string).strip()

        if question['required'] and not answer:
            while not answer:
                print 'Sorry, {} is a required value'.format(question['key'])
                answer = raw_input(question_string).strip()

        if answer and question['is_array']:
            answer = answer.split(',')

        return answer or question['default']
