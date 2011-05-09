	function ForceNumericInput(This, AllowDot, AllowMinus,e)
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

        if(window.event){
        var code = event.keyCode;
        }else{
        var code = e.keyCode;
        }
        
        switch(code)
        {
            case 8:     // backspace
            case 37:    // left arrow
            case 39:    // right arrow
            case 46:    // delete
                if(window.event) event.returnValue=true;
                return;
        }
        if(code == 189)     // minus sign
        {
        	if(AllowMinus == false)
        	{
                if(window.event){
                event.returnValue=false;
                }else{
                StopEvent(e);
                }
                return;
            }


            // wait until the element has been updated to see if the minus is in the right spot
            var s = "ForceNumericInput(document.getElementById('"+This.id+"'),"+AllowMinus+","+AllowDot+","+e+")";
            setTimeout(s, 250);
            return;
        }
        if(AllowDot && code == 190)
        {
            if(This.value.indexOf(".") >= 0)
            {
            	// don't allow more than one dot
                if(window.event){
                event.returnValue=false;
                }else{
                StopEvent(e);
                }
                return;
            }
            if(window.event) event.returnValue=true;
            return;
        }
        // allow character of between 0 and 9
        if(code >= 48 && code <= 57)
        {
            if(window.event) event.returnValue=true;
            return;
        }
        if(window.event){
        event.returnValue=false;
        }else{
        StopEvent(e);
        }
	}
	
	function StopEvent(pE)
    {
    if (!pE)
    if (window.event)
    pE = window.event;
    else
    return;
    if (pE.cancelBubble != null)
    pE.cancelBubble = true;
    if (pE.stopPropagation)
    pE.stopPropagation();
    if (pE.preventDefault)
    pE.preventDefault();
    if (window.event)
    pE.returnValue = false;
    if (pE.cancel != null)
    pE.cancel = true;
    } // StopEvent
	
