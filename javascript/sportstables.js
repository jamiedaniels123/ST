$('#index').live('pageinit',function(event){
	if(screen.width > 500){
		$('div.desktop-only').css('display', 'block');	
	}
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
	});
});

$('#existing').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
	});
});

$('#new').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
        var tn=document.forms["create_table_form"]["name"].value;     
        if (tn==null || tn=="" || tn==" "){
        	document.forms["create_table_form"]["name"].value = 'Unnamed table';
        }
	});
});

$('#table').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
	});
});

$('#teams').live('pageinit',function(event){	
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
        var tn=document.forms["add_team_form"]["name"].value;     
        if (tn==null || tn=="" || tn==" "){
        	document.forms["add_team_form"]["name"].value = 'Unnamed team';
        }		
	});
});

$('#results').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
		if ($(this).attr('name') == 'add_result_form'){
		    var hts=document.forms["add_result_form"]["home_team_score"].value;
		    var ats=document.forms["add_result_form"]["away_team_score"].value;
		    var htid=document.forms["add_result_form"]["home_team"].value;
		    var atid=document.forms["add_result_form"]["away_team"].value;      
		    if (hts==null || hts=="" || !IsNumeric(hts)){
			    $('input[type=submit]', this).removeAttr('disabled');
		        alert("Home team score must be a number");
		        return false;
		    }
		    if (ats==null || ats=="" || !IsNumeric(ats)){
			    $('input[type=submit]', this).removeAttr('disabled');
		        alert("Away team score must be a number");        
		        return false;
		    }
		    if (htid==atid){
			    $('input[type=submit]', this).removeAttr('disabled');
		        alert("A team can't play against itself");	        
		        return false;
		    }
		}
	});
});

$('#share').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
	});
});

$('#viewer').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
	});
});

$('#displaymessage').live('pageinit',function(event){
	$('form').submit(function(){
		// On submit disable its submit button
		$('input[type=submit]', this).attr('disabled', 'disabled');
	});
});

function clearDefaultText(formID, elementID, startValue){
	var form = formID;
	var element = elementID;
	if (document.forms[form][element].value == startValue){
        document.forms[form][element].value = '';
	}
}

function IsNumeric(sText){
    var ValidChars = "0123456789";
    var IsNumber=true;
    var Char;
    for (i = 0; i < sText.length && IsNumber == true; i++){ 
      Char = sText.charAt(i); 
      if (ValidChars.indexOf(Char) == -1){
        IsNumber = false;
      }
    }
    return IsNumber;
}

