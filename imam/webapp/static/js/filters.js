$(function () {
    var dateFormat = "dd/mm/yyyy";

    $('.form-reset').click(function () {
        form = $(this).parents('form');
        $('input[name!="csrfmiddlewaretoken"]', form).each(function (id, el) {
            $(el).val("");
        });
        $('select', form).each(function (id, el) {
            $(el).val("");
        });
        $(form).submit();
    });

    $('.form-submit').click(function () {
        form = $(this).parents('form');
        $(form).submit();
    });

    // $('.select-two').select2(
    // 	{ width: 'element' }
    // );
    $('.select-two').each(function (index, elem) {
        $(elem).select2({
            //width: "resolve",
            dropdownAutoWidth: true,
            placeholder: S(elem.name).humanize().capitalize()
        });
    });
    if ($('#id_location').val() === null || $('#id_location').val() === 0)
        $('#id_location').val(1)
    $('#id_location').select2({
        dropdownAutoWidth: true,
        ajax: {
            url: "/locations/find",
            data: function (term, page) {
                return {
                    q: term // search term
                };
            },
            results: function (data, page) {
                var i, results = [];
                for (i = 0; i < data.length; i++) {

                    if (i === 0 || data[i - 1][2] !== data[i][2]) {
                        results.push({
                            text: data[i][2],
                            children: []
                        });
                    }
                    results[results.length - 1].children.push({
                        text: data[i][1],
                        id: data[i][0]
                    });
                }
                return {results: results};
            }
        },
        initSelection: function (element, callback) {
            var pk = $(element).val();
            $.ajax({
                url: "/locations/find?pk=" + pk,
                success: function (data) {
                    callback({id: pk, text: data});
                }
            });

        }
    });

    // Get rid of the form-control style from the panel filter (inelegant).
    $('.panel .form-group div.form-control').removeClass('form-control');

    // Activate date pickers for all date fields (e.g. Stock reports)
    if (typeof $.fn.datepicker !== 'undefined' && $.isFunction(jQuery.fn.datepicker)) {
        $(document).ready(function () {
            $('.dateinput').datepicker({
                format: dateFormat,
                todayHighlight: true,
                todayBtn: true
            });
        });
    }
    ;
});
