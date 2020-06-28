# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from lxml import etree

import datetime
from dateutil import tz
import pytz
import time
from string import Template
from datetime import datetime, timedelta
from odoo.exceptions import  Warning
from pdb import set_trace as bp

from itertools import groupby
from operator import itemgetter

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__) # Need for message in console.

# class ProjectTaskAncestor(models.Model):
#
#     _name = 'project.task.ancestor'
#
#
#     task_id = fields.Many2one('project.task', 'Task')
#     ancestor_task_id = fields.Many2one('project.task', 'Parent Task', required=True, domain = "[('project_id','=', parent.project_id)]")
#
#     _sql_constraints = [
#         ('project_task_ancestor_uniq', 'unique(task_id, ancestor_task_id)', 'Must be unique record.'),
#
#     ]

class ProjectTaskPredecessor(models.Model):

    _name = 'project.task.predecessor'

    @api.model
    def _get_link_type(self):
        value = [
            ('FS', _('Finish to Start')),
            ('SS', _('Start to Start')),
            ('FF', _('Finish to Finish')),
            ('SF', _('Start to Finish')),

        ]

        return value


    task_id = fields.Many2one('project.task', 'Task')
    parent_task_id = fields.Many2one('project.task', 'Parent Task', required=True, ondelete='restrict', domain = "[('project_id','=', parent.project_id)]")
    type = fields.Selection('_get_link_type',
                            string='Type',
                            required=True,)

    # project_id = fields.Many2one('project.project', 'Project', related='task_id.project_id', store=True)

    _sql_constraints = [
        ('project_task_link_uniq', 'unique(task_id, parent_task_id, type)', 'Must be unique.'),

    ]


class ProjectTaskNative(models.Model):
    _name = "project.task"
    _inherit = ['project.task']

    @api.model
    def _get_schedule_mode(self):
        value = [
            ('auto', _('Auto')),
            ('manual', _('Manual')),
        ]
        return value

    @api.model
    def _get_constrain_type(self):
        value = [
            ('asap', _('As Soon As Possible')),
            ('fnet', _('Finish No Earlier Than')),
            ('fnlt', _('Finish No Later Than')),
            ('mso', _('Must Start On')),
            ('mfo', _('Must Finish On')),
            ('snet', _('Start No Earlier Than')),
            ('snlt', _('Start No Later Than')),
        ]
        return value


    #link
    predecessor_ids = fields.One2many('project.task.predecessor', 'task_id', 'Links')
    predecessor_count = fields.Integer(compute='_compute_predecessor_count', string='Predecessor', store=True)

    #sorting
    sorting_seq = fields.Integer(string='Sorting Seq.')
    sorting_level = fields.Integer('Sorting Level', default=0)
    sorting_level_seq = fields.Integer('Sorting Level Seq.', default=0)


    #Gantt
    is_milestone = fields.Boolean("Mark as Milestone", default=False)
    on_gantt = fields.Boolean("Task name on gantt", default=False)
    date_finished = fields.Datetime('Done Date')

    #info - autoplanning
    duration = fields.Integer(
        'Duration', compute='_compute_duration',
        readonly=True, store=True)

    #scheduler
    schedule_mode = fields.Selection('_get_schedule_mode',
                            string='Schedule Mode',
                            required=True,
                            default='manual')

    #constrain
    constrain_type = fields.Selection('_get_constrain_type',
                            string='Constraint Type',
                            required=True,
                            default='asap')
    constrain_date = fields.Datetime('Constraint Date')



    plan_action = fields.Integer(compute='_compute_plan_action', string='Plan Action', store=True)
    plan_duration = fields.Integer(string='Plan Duration', default=86400)


    @api.onchange('project_id')
    def _onchange_project(self):
        if hasattr(super(ProjectTaskNative, self), '_onchange_project'):
            if self._origin.id:
                if self.env['project.task.predecessor'].search(
                        ['|', ('task_id', '=', self._origin.id), ('parent_task_id', '=', self._origin.id), (('parent_task_id', '=', self._origin.id))], limit=1):
                    raise UserError(_(
                        'You can not change a Project for task.\nPlease Delete - Predecessor: for parent or child.'))

                if self.search([('parent_id', '=', self._origin.id)], limit=1):
                    raise UserError(_(
                        'You can not change a Project for Task.\nPlease Delete or Remove - sub tasks first.'))

            super(ProjectTaskNative, self)._onchange_project()


    @api.depends("predecessor_ids")
    def _compute_predecessor_count(self):

        for task in self:
            task.predecessor_count = len(task.predecessor_ids)

    @api.model
    def scheduler_plan(self, project_id):

        search_tasks = self.env['project.task'].sudo().search(['&',('project_id', '=', project_id), ('predecessor_count', '=', 0)])
        for stask in search_tasks:
            self._scheduler_work(stask)

        return True



    def _scheduler_work(self, task):

        search_objs = self.env['project.task.predecessor'].sudo().search([('parent_task_id', '=', task.id)])

        # original_date_start = self._origin.date_start
        # original_date_end = self._origin.date_end

        for obj in search_objs:
            vals = {}

            # obj_date_start = fields.Datetime.from_string(obj.task_id.date_start)
            # obj_date_end = fields.Datetime.from_string(obj.task_id.date_end)
            # if not obj_date_end:
            #     obj_date_end = obj_date_start + timedelta(days=1)
            # diff = obj_date_end - obj_date_start

            plan_duration = obj.task_id.plan_duration
            if plan_duration == 0:
                plan_duration = 86400 # 1 day
            diff = timedelta(seconds=plan_duration)

            # task_date_start = task.date_start
            # task_date_end = task.date_end
            search_data_objs = self.env['project.task.predecessor'].sudo().search([('task_id', '=', obj.task_id.id)])
            # Schedule Mode
            if obj.type == "FS":
                date_list = []

                for date_obj in search_data_objs:
                    if date_obj.type == "FS":
                        date_list.append(fields.Datetime.from_string(date_obj.parent_task_id.date_end))

                new_date_start = max(date_list)
                new_date_end = new_date_start + diff

                vals['date_start'] = fields.Datetime.to_string(new_date_start)
                vals['date_end'] = fields.Datetime.to_string(new_date_end)

            if obj.type == "SS":
                date_list = []
                for date_obj in search_data_objs:
                    if date_obj.type == "SS":
                        date_list.append(fields.Datetime.from_string(date_obj.parent_task_id.date_start))

                new_date_start = min(date_list)
                new_date_end = new_date_start + diff

                vals['date_start'] = fields.Datetime.to_string(new_date_start)
                vals['date_end'] = fields.Datetime.to_string(new_date_end)

            if obj.type == "FF":
                date_list = []
                for date_obj in search_data_objs:
                    if date_obj.type == "FF":
                        date_list.append(fields.Datetime.from_string(date_obj.parent_task_id.date_end))

                new_date_end = max(date_list)
                new_date_start = new_date_end - diff

                vals['date_start'] = fields.Datetime.to_string(new_date_start)
                vals['date_end'] = fields.Datetime.to_string(new_date_end)

                # n_start_end = fields.Datetime.from_string(task_date_end) - diff
                #
                # vals['date_start'] = fields.Datetime.to_string(n_start_end)
                # vals['date_end'] = task_date_end

            if obj.type == "SF":
                date_list = []

                for date_obj in search_data_objs:
                    if date_obj.type == "SF":
                        date_list.append(fields.Datetime.from_string(date_obj.parent_task_id.date_start))

                new_date_end = max(date_list)
                new_date_start = new_date_end - diff

                vals['date_start'] = fields.Datetime.to_string(new_date_start)
                vals['date_end'] = fields.Datetime.to_string(new_date_end)

                # n_start_end = fields.Datetime.from_string(task_date_start) - diff
                #
                # vals['date_start'] = fields.Datetime.to_string(n_start_end)
                # vals['date_end'] = task_date_start

            if obj.task_id:

                if obj.task_id.constrain_type not in "asap" and obj.task_id.constrain_date and vals:

                    # parent_task_date_start = fields.Datetime.from_string(task_date_start)
                    # parent_task_date_end = fields.Datetime.from_string(task_date_end)

                    constrain_date = fields.Datetime.from_string(obj.task_id.constrain_date)

                    if obj.task_id.constrain_type == "fnet":  # Finish No Early Than

                        sheduled_task_data = fields.Datetime.from_string(vals['date_end'])

                        if sheduled_task_data < constrain_date:
                            task_date_end = fields.Datetime.to_string(constrain_date)
                            new_date = fields.Datetime.to_string(constrain_date - diff)
                            vals['date_start'] = new_date
                            vals['date_end'] = task_date_end

                    if obj.task_id.constrain_type == "fnlt":  # Finish No Later Than

                        sheduled_task_data = fields.Datetime.from_string(vals['date_end'])

                        if sheduled_task_data > constrain_date:
                            task_date_end = fields.Datetime.to_string(constrain_date)
                            new_date = fields.Datetime.to_string(constrain_date - diff)
                            vals['date_start'] = new_date
                            vals['date_end'] = task_date_end

                    if obj.task_id.constrain_type == "mso":  # Must Start On


                        task_date_start = fields.Datetime.to_string(constrain_date)
                        new_date = fields.Datetime.to_string(constrain_date + diff)
                        vals['date_start'] = task_date_start
                        vals['date_end'] = new_date

                    if obj.task_id.constrain_type == "mfo":  # Must Finish On


                        task_date_end = fields.Datetime.to_string(constrain_date)
                        new_date = fields.Datetime.to_string(constrain_date - diff)
                        vals['date_start'] = new_date
                        vals['date_end'] = task_date_end

                    if obj.task_id.constrain_type == "snet":  # Start No Earlier Than


                        sheduled_task_data = fields.Datetime.from_string(vals['date_start'])

                        if sheduled_task_data < constrain_date:
                            task_date_start = fields.Datetime.to_string(constrain_date)
                            new_date = fields.Datetime.to_string(constrain_date + diff)
                            vals['date_start'] = task_date_start
                            vals['date_end'] = new_date
                            obj.task_id.write(vals)
                            # task_date_end = fields.Datetime.to_string(constrain_date)

                    if obj.task_id.constrain_type == "snlt":  # Start No Later Than

                        sheduled_task_data = fields.Datetime.from_string(vals['date_start'])

                        if sheduled_task_data > constrain_date:
                            task_date_start = fields.Datetime.to_string(constrain_date)
                            new_date = fields.Datetime.to_string(constrain_date + diff)
                            vals['date_start'] = task_date_start
                            vals['date_end'] = new_date
                            obj.task_id.write(vals)
                            # task_date_end = fields.Datetime.to_string(constrain_date)

                if obj.task_id.schedule_mode == "auto" and vals:
                    vals['plan_action'] = False
                    obj.task_id.write(vals)
                    self._scheduler_work(obj.task_id)


    @api.depends("predecessor_ids.task_id", "predecessor_ids.type", "constrain_type", "constrain_date" )
    def _compute_plan_action(self):
        for task in self:
            task.plan_action = True



    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for task in self:

            if task.date_end:
                diff = fields.Datetime.from_string(task.date_end) - fields.Datetime.from_string(task.date_start)
                task.duration = diff.total_seconds()
            else:
                task.duration = 0.0

    # nodes = [
    #     {'id': 1, 'parent': None},
    #     {'id': 2, 'parent': 1},
    #     {'id': 3, 'parent': 1},
    #     {'id': 4, 'parent': 2},
    #     {'id': 5, 'parent': 2},
    #     {'id': 6, 'parent': 5},
    #     {'id': 7, 'parent': 6},
    #     {'id': 8, 'parent': 3}
    # ]

    # node_list = []

    # def p_tree_onfly(self, query, parent): # array with inside array for sorting only in level.
    #     parent['children'] = []
    #     for item in query:
    #         if item['parent'] == parent['id']:
    #             parent['children'].append(item)
    #             self.p_tree_onfly(query, item)
    #     return parent

    # def pop_list(self, nodes=None, parent=None, node_list=None):
    #     next_parent = False
    #     if parent is None:
    #         return node_list
    #     node_list.append([])
    #     for node in nodes:
    #         if node['parent'] == parent:
    #             node_list[-1].append(node)
    #         if node['id'] == parent:
    #             next_parent = node['parent']
    #
    #
    #     if next_parent:
    #
    #         self.pop_list(nodes, next_parent, node_list)
    #     return node_list





    @api.multi
    def unlink(self):

        if self.search([('parent_id', 'in', self.ids)],limit=1):
            raise UserError(_(
                    'You can not delete a Parent Task.\nPlease Delete - sub tasks first.'))
        return super(ProjectTaskNative, self).unlink()



    @api.model
    def create(self, vals):

        get_parent_id = vals.get('parent_id', None)

        new_id = super(ProjectTaskNative, self).create(vals)

        if get_parent_id:

            self.do_sorting(new_id.subtask_project_id.id)

        return new_id


    @api.multi
    def write(self, vals):

        get_parent_id = vals.get('parent_id', None)

        result = super(ProjectTaskNative, self).write(vals)

        if get_parent_id is not None and result:


            self.do_sorting(self.subtask_project_id.id)

        return result

    
    @api.one
    @api.depends('parent_id')
    def _compute_sorting(self):
        self.do_sorting(self.subtask_project_id.id)


    def tree_onfly(self, query, parent): # array with inside array for sorting only in level.
        parent['children'] = []
        for item in query:
            if item['parent_id'] == parent['id']:
                parent['children'].append(item)
                self.tree_onfly(query, item)
        return parent


    def flat_onfly(self, object, level=0):  # recusive search sub level.
        result = []

        def _get_rec(object, level, parent=None):

            object = sorted(object, key=itemgetter('sorting_level_seq'))
            for line in object:

                res = {}
                res['id'] = '{}'.format(line["id"])
                res['name'] = u'{}'.format(line["name"])
                res['parent_id'] = u'{}'.format(line["parent_id"])
                res['sorting_level_seq'] = line["sorting_level_seq"]
                res['level'] = '{}'.format(level)

                result.append(res)

                if line["children"]:

                    if level < 16:
                        level += 1
                        parent = line["id"]
                    _get_rec(line["children"], level, parent)
                    if level > 0 and level < 16:
                        level -= 1
                        parent = None

            return result

        children = _get_rec(object, level)

        return children


    def do_sorting(self, subtask_project_id,):  # recusive search sub level.

        search_objs = self.sudo().search([('subtask_project_id', '=', subtask_project_id)])

        line_datas = []
        for search_obj in search_objs:
            res = {}
            res['id'] = '{}'.format(search_obj.id)
            res['name'] = u'{}'.format(search_obj.name)
            res['parent_id'] = u'{}'.format(search_obj.parent_id.id)
            res['sorting_level_seq'] = search_obj.sorting_level_seq

            line_datas.append(res)

        root = {'id': "False"}
        tree_onfly = self.tree_onfly(line_datas, root)

        flat_onfly = self.flat_onfly(tree_onfly["children"])

        for index, line in enumerate(flat_onfly):

            var_data = {

                "sorting_seq" : index + 1,
                "sorting_level" : int(line["level"])
            }

            task_obj = self.env['project.task']
            task_obj_search = task_obj.sudo().search([('id', '=', int(line["id"]))])
            task_obj_search.sudo().write(var_data)



    # def get_children(self, object, level=0):  # recusive search sub level.
    #     result = []
    #
    #     def _get_rec(object, level, parent=None):
    #         for line in object:
    #
    #             res = {}
    #             res['id'] = '{}'.format(line.id)
    #             res['level'] = '{}'.format(level)
    #             res['name'] = u'{}'.format(line.name)
    #             res['parent_id'] = u'{}'.format(line.parent_id.id)
    #             res['sorting_seq'] = '{}'.format(line.sorting_seq or 0)
    #
    #
    #             result.append(res)
    #
    #             if line.child_ids:
    #
    #                 if level < 16:
    #                     level += 1
    #                     parent = line.id
    #                 _get_rec(line.child_ids, level, parent)
    #                 if level > 0 and level < 16:
    #                     level -= 1
    #                     parent = None
    #
    #         return result
    #
    #     children = _get_rec(object, level)
    #
    #     return children



    @api.model
    def sorting_update(self, sorting_ids, subtask_project_id, project_id):

        for sort in sorting_ids:
            id = sort["id"]
            seq = sort["seq"]

            var_data = {
                "sorting_level_seq" : int(seq)
            }
            task_obj_search = self.sudo().search([('id', '=', int(id))])
            task_obj_search.sudo().write(var_data)

        if not subtask_project_id:

            if project_id:
                project = self.env['project.project'].sudo().search([('id', '=', project_id)])
                if project.id:
                    project.sudo().write({"subtask_project_id": project_id})
                    self.do_sorting(project_id)

        if subtask_project_id:
            self.do_sorting(subtask_project_id[0])

    @api.model
    def childs_get(self, ids_field_name, ids, fields):

        test = "OK"
        return test



