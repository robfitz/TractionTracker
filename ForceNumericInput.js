	function ForceNumericInput(This, AllowDot, AllowMinus)
	{
		if(arguments.length == 1)
		{
        	var s = This.value;
        	// if "-" exists then it better be the 1st character
        	var i = s.lastIndexOf("-");
        	if(i == -1)
            	return;
        	if(i != 0)
           		This.value = s.substring(0,i)+s.substring(i+1);
           	return;
        }

        var code = event.keyCode;
        switch(code)
        {
            case 8:     // backspace
            case 37:    // left arrow
            case 39:    // right arrow
            case 46:    // delete
                event.returnValue=true;
                return;
        }
        if(code == 189)     // minus sign
        {
        	if(AllowMinus == false)
        	{
                event.returnValue=false;
                return;
            }


            // wait until the element has been updated to see if the minus is in the right spot
            var s = "ForceNumericInput(document.getElementById('"+This.id+"'))";
            setTimeout(s, 250);
            return;
        }
        if(AllowDot && code == 190)
        {
            if(This.value.indexOf(".") >= 0)
            {
            	// don't allow more than one dot
                event.returnValue=false;
                return;
            }
            event.returnValue=true;
            return;
        }
        // allow character of between 0 and 9
        if(code >= 48 && code <= 57)
        {
            event.returnValue=true;
            return;
        }
        event.returnValue=false;
	}
