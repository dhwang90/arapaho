function multipleFields(lexid){

    var add_button      = $(".add_field_button"+lexid); //Add button ID
    var wrapper         = $(".input_fields_wrap"+lexid); //Fields wrapper
    var max_fields      = 5; //maximum input boxes allowed


    var x = 1; //initial text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            var n = $(this).attr("n");
            var add_html = '<span><label>&nbsp;</label> <input type="text" name="'+n+'" size="20" class="short"/>'+
                       '<a href="#" class="remove_field">(remove)</a><br/></span>\n';
            $(wrapper).append(add_html); //add input box
        }
    });

    $(wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('span').remove(); x--;
    });

}

function multipleDerivations(lexid){

    var add_button      = $(".add_deriv_button"+lexid); //Add button ID
    var wrapper         = $(".input_deriv_wrap"+lexid); //Fields wrapper
    var max_fields      = 5; //maximum input boxes allowed


    var x = 1; //initial text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            var add_html = '<div class="derivations">\n'+
                        '<select name="deriv_type" class="deriv_type">\n'+
                            '<option value="0">--Select--</option>\n'+
                            '<option value="pl" class="noun">pl</option>\n'+
                            '<option value="obv.sg" class="na">obv sg</option>\n'+
                            '<option value="obv.pl" class="na">obv pl</option>\n'+
                            '<option value="poss3" class="noun">3 poss</option>\n'+
                            '<option value="loc" class="noun">loc</option>\n'+
                            '<option value="voc" class="na">voc</option>\n'+
                            '<option value="s3" class="verb">3 s</option>\n'+
                        '</select>\n'+
                        '<input name="deriv_value" size="20" type="text" class="short">\n'+
                        '<a href="#" class="remove_field">(remove)</a>'+
                        '</div>';

            $(wrapper).append(add_html); //add input box
        }
    });

    $(wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('div').remove(); x--;
    });

}

function multipleSenses(lexid){
    var add_sense      = $(".add_sense"+lexid); //Add button ID
    var sense_wrapper  = $(".sense_wrap"+lexid); //Fields wrapper
    var max_senses     = 10; //maximum input boxes allowed

    var sense_cnt = 1; //initial text box count
    $(add_sense).click(function(e){ //on add input button click
        e.preventDefault();
        if(sense_cnt < max_senses){ //max input box allowed
            sense_cnt++; //text box increment
            var add_html = '<div class="senses">\n'+
                       '<h4>New Sense: </h4> <a href="#" class="remove_sense">(remove)</a><br>'+
                       '<label>definition<span style="color:red">*</span> (de):</label> <input name="definition[]" size="80" type="text" class="required"><br>'+
                       '<label>usage (ue):</label> <input name="usage[]" size="80" type="text"><br>'+
                       '<label>scientific (sc):</label> <input name="scientific[]" size="80" type="text"><br>'+
                       '<label>synonym (sy):</label> <input name="synonym[]" size="80" type="text"><br>'+
                       '<label>note (nt):</label> <input name="note[]" size="80" type="text"><br>'+
                       '<label>sources (so):</label> <input name="sources[]" size="80" type="text"><br>'+
                       '</div>';
            $(sense_wrapper).append(add_html); //add input box
        }
    });

    $(sense_wrapper).on("click",".remove_sense", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('div').remove(); sense_cnt--;
    });
}

function modifyPos(num,outkey){
    var saveModify = [];
    $("button#modifyButton"+num).click(function(){
        if($("#modify"+num).is(":visible")) {
            $("#modify"+num).css( "display","none");
        } else {
            $(".modify").css("display","none");

            // don't re-query the server if run once. just hide.
            if (jQuery.inArray(num,saveModify) == -1) {
                $.ajax({
                    url: '/pos_modify',
                    type: "POST",
                    cache: false,
                    data: { key: outkey,  main:  $("input#main"+num).val(), high:$("input#high"+num).val(), low:$("input#low"+num).val() },
                    success: function(html) {
                        $("#modify"+num).html(html);
                    }
                });
                saveModify.push(num)
            }
            $("#modify"+num).css( "display","block");
        }
    });
}

function requireFields(){
    $("#submit_data").click(function(event){
        $( ".required" ).each(function() {
            if ($(this).val() == '') {
                event.preventDefault();
                $("#required_fields_error").removeClass("error").addClass("error_show");
                return false;
            }
        });
    });
}

function errorCheck(entity_type){
    // WARNING: this only works for the current new form setup with button type=button.


    $("button#submit_data").click(function(event){
        var error_found = false;
        $( ".required" ).each(function() {
            if ($(this).val() == '') {
                error_found = true;
                return false;
            }
        });

        if (error_found) {
            $("#required_fields_error").removeClass("error").addClass("error_show");
        } else {
            $("#required_fields_error").removeClass("error_show").addClass("error");
            if (entity_type == 'pos') {
                $.ajax({
                    url: '/error_check',
                    type: "POST",
                    cache: false,
                    data: { 'entity_type': entity_type, main: $("input#main").val(), high: $("input#high").val(), low: $("input#low").val() },
                    success: function(entity_item) {
                        if (entity_item == 'None') {
                            $("#entry").submit();
                        }else{
                            $("#duplicate_error").removeClass("error").addClass("error_show");
                        }
                    }
                });
            } else {
                $.ajax({
                    url: '/error_check',
                    type: "POST",
                    cache: false,
                    data: { 'entity_type': entity_type, lex: $("input#lex").val(), pos: $("input#pos").val() },
                    success: function(entity_item) {
                        if (entity_item == 'None') {
                            $("#entry").submit();
                        }else{
                            $("#duplicate_error").removeClass("error").addClass("error_show");
                        }
                    }
                });
            }
        }
    });

    $("button#duplicate_save").click(function(){
        $("#entry").submit();
        $("#duplicate_error").removeClass("error_show").addClass("error");
    });

    $("button#duplicate_cancel").click(function(){
        $("#duplicate_error").removeClass("error_show").addClass("error");
    });
}

function dataChanged(lexid){
    //activate if data changed
    $('form#modify'+lexid)
    .each(function(){
        $(this).data('serialized', $(this).serialize())
    })
    .on('change input', function(){
        $(this)
            .find('input:submit, button:submit')
                .attr('disabled', $(this).serialize() == $(this).data('serialized'))
        ;
     })
    .find('input:submit, button:submit').attr('disabled', true);
}

function submitEntry(lexid){
    $('#modify'+lexid).on('submit',function(e) {
        // prevent default submit
        e.preventDefault();
        alert($(this).serialize());
        $.post(this.action,$(this).serialize());
    });
}

function slidingDiv(divname) {
    $("#"+divname).click(function(){
        var $div = $('#' + $(this).data('href'));
        $('.modify').not($div).hide();
        $div.slideToggle();
   });
 }

function resetSearch() {
    $( "#resetSearch" ).click(function(e) {
        $("div#lex_search input[type=text]").each(function() {
           $(this).val('');
        });
    });
 }

