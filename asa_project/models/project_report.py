from odoo import fields, models, tools


class ReportProject(models.Model):
    _name = "report.project.task"
    _description = "Tasks by  project"
    _order = 'name desc, project_id'
    _auto = False

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    name = fields.Char(string='Task Title', readonly=True)
    date = fields.Date(string='Date Progres', readonly=True)
    plan_line = fields.Float(string='Plan Weight Line(%)', readonly=True)
    actual_line = fields.Float(string='Actual Weight Line(%)', readonly=True)
    bobot = fields.Float(string='Plan Weight (%)', readonly=True)
    bobot_actual = fields.Float(string='Actual Weight (%)', readonly=True)
    
   

    def _select(self):
        select_str = """
             SELECT min(t.id) as id,
                    p.date as date,
                    t.name as name,
                    p.bobot_plan_line as plan_line,
                    p.bobot_actual_line as actual_line,
                    t.project_id,
                    t.bobot,
                    t.bobot_actual
        """
        return select_str

    def _from(self):
        from_str = """
                project_progres p
                      join project_task t on (p.task_id=t.id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY t.project_id,
                     date,
                     name,
                     plan_line,
                     actual_line,
                     t.bobot,
                     t.bobot_actual
                    
        """
        return group_by_str

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
        
        