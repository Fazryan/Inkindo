odoo.define('web.web_widget_time_delta', function(require) {
    "use strict";

    var core = require('web.core');
    var widget = require('web.form_widgets');
    var FormView = require('web.FormView');
    var list_widget_registry = core.list_widget_registry;
    // var humanizeDuration = require('humanize-duration');

    var QWeb = core.qweb;
    var _lt = core._lt;

    // var _super_getDir = jscolor.getDir.prototype;
    // jscolor.getDir = function () {
    //     var dir = _super_getDir.constructor();
    //     if (dir.indexOf('web_widget_color') === -1) {
    //         jscolor.dir = 'web_widget_color/static/lib/jscolor/';
    //     }
    //     return jscolor.dir;
    // };

    var FieldTimeDelta = widget.FieldChar.extend({
        template: 'FieldTimeDelta',
        widget_class: 'oe_form_field_time_delta',
        is_syntax_valid: function () {
            var $input = this.$('input');
            if (!this.get("effective_readonly") && $input.size() > 0) {
                var val = $input.val();
                var isOk = /^\d+$/.test(val);
                if (!isOk) {
                    return false;
                }
                try {
                    this.parse_value(this.$('input').val(), '');
                    return true;
                } catch (e) {
                    return false;
                }
            }
            return true;
        },
        store_dom_value: function() {
            if (!this.silent) {
                if (!this.get('effective_readonly') &&
                    this.$('input').val() !== '' &&
                    this.is_syntax_valid()) {
                    // We use internal_set_value because we were called by
                    // ``.commit_value()`` which is called by a ``.set_value()``
                    // itself called because of a ``onchange`` event
                    this.internal_set_value(
                        this.parse_value(
                            parseInt(this.$('input').val(), 10))
                        );
                }
            }
            },
        render_value: function () {

            var show_value = this.format_value(this.get('value'), this);
            if (!this.get("effective_readonly")) {
                var $input = this.$el.find('input');
                $input.val(show_value);

                $input.durationPicker({
                    showSeconds: true,
                    onChanged: function (newVal) {
                    $input.val(newVal);
                }
                });


            } else {
                // var $duration = $('<input readonly type="text" class="form-control" id="duration" value='+show_value+'>');
                // this.$el.append($duration);
                // var $input2 = this.$el.find('input');
                // $input2.durationPicker({
                //      showSeconds: true
                // });
                var total = parseInt(show_value, 10);
                this.$(".oe_form_char_content").text(humanizeDuration(total*1000));

            }


        }
    });


    var FieldTimeDeltaList = list_widget_registry.get('field').extend({

        _format: function (row_data, options) {

            var value = row_data[this.id].value;

            if (value === 0){
                return "-"
            }

            var total = parseInt(value, 10);

            return humanizeDuration(total*1000)
        }



   });


    list_widget_registry
        .add('field.time_delta_list', FieldTimeDeltaList);

    core.form_widget_registry.add('time_delta', FieldTimeDelta);

    /*
     * Init jscolor for each editable mode on view form
     */
    FormView.include({
        on_button_edit: function () {
            this._super();

        },
        on_button_create: function () {
            this._super();

        }
    });

    return {
        FieldTimeDelta: FieldTimeDelta
    };
});
