Timedelta widget for Odoo web client
================================


Features
========


* Display the color on form view when you are not editing it

  |formview|

* Display the color on list view to quickly find what's wrong!

  |listview|


Usage
=====

You need to declare a integer field Default set second.

    duration = fields.integer(
        string="Duration",
        help="Set Duration",
        default="60"
    )


In the view declaration, put widget='time_delta' for Form and  widget='time_delta_list' for List

    ...
    <field name="arch" type="xml">
        <tree string="View name">
            ...
            <field name="duration" widget="time_delta_list"/>
            ...
        </tree>
    </field>
    ...

    ...
    <field name="arch" type="xml">
        <form string="View name">
            ...
            <field name="duration" widget="time_delta"/>
            ...
        </rom>
    </field>
    ...

