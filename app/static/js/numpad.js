var numpad = {
  /* [INIT - DRAW THE ON-SCREEN NUMPAD] */
  selector : null, // will hold the entire on-screen numpad
  display : null, // will hold the numpad display
  zero : null, // will hold the zero button
  dot : null, // will hold the dot button
  init : function () {
    // CREATE THE NUMPAD
    numpad.selector = document.createElement("div");
    numpad.selector.id = "numpad-back";
    var wrap = document.createElement("div");
    wrap.id = "numpad-wrap";
    numpad.selector.appendChild(wrap);

    // ATTACH THE NUMBER DISPLAY
    numpad.display = document.createElement("input");
    numpad.display.id = "numpad-display";
    numpad.display.readOnly = true;
    wrap.appendChild(numpad.display);

    // ATTACH BUTTONS
    var buttons = document.createElement("div"),
        button = null,
        append = function (txt, fn, css) {
          button = document.createElement("div");
          button.innerHTML = txt;
          button.classList.add("numpad-btn");
          if (css) {
            button.classList.add(css);
          }
          button.addEventListener("click", fn);
          buttons.appendChild(button);
        };
    buttons.id = "numpad-btns";
    // First row - 7 to 9, delete.
    for (var i=7; i<=9; i++) {
      append(i, numpad.digit);
    }
    append("&#10502;", numpad.delete, "ng");
    // Second row - 4 to 6, clear.
    for (var i=4; i<=6; i++) {
      append(i, numpad.digit);
    }
    append("Clear", numpad.reset, "ng");
    // Third row - 1 to 3, cancel.
    for (var i=1; i<=3; i++) {
      append(i, numpad.digit);
    }
    append("Exit", numpad.hide, "cx");
    // Last row - 0, dot, ok
    append(0, numpad.digit, "zero");
    numpad.zero = button;
    append(".", numpad.dot);
    numpad.dot = button;
    append("OK", numpad.select, "ok");
    // Add all buttons to wrapper
    wrap.appendChild(buttons);
    document.body.appendChild(numpad.selector);
  },

  /* [ATTACH TO INPUT] */
  attach : function (opt) {
  // attach() : attach numpad to target input field

    var target = document.getElementById(opt.id);
    if (target!=null) {
      // APPEND DEFAULT OPTIONS
      if (opt.readonly==undefined || typeof opt.readonly!="boolean") { opt.readonly = true; }
      if (opt.decimal==undefined || typeof opt.decimal!="boolean") { opt.decimal = true; }
      if (opt.max==undefined || typeof opt.max!="number") { opt.max = 16; }
      if (opt.separator==undefined) { opt.separator = null; }
      if (opt.input_type==undefined) { opt.input_type = 'text'; }

      // SET READONLY ATTRIBUTE ON TARGET FIELD
      if (opt.readonly) { target.readOnly = true; }

      // ALLOW DECIMALS?
      target.dataset.decimal = opt.decimal ? 1 : 0;

      target.dataset.separator = opt.separator;
      target.dataset.input_type = opt.input_type;
        
      // MAXIMUM ALLOWED CHARACTERS
      target.dataset.max = opt.max;

      // SHOW NUMPAD ON CLICK
      target.addEventListener("click", numpad.show);
    } else {
      console.log(opt.id + " NOT FOUND!");
    }
  },

  target : null, // contains the current selected field
  dec : true, // allow decimals?
  max : 16, // max allowed characters
  show : function (evt) {
  // show() : show the number pad

    // Set current target field
    numpad.target = evt.target;

    // Show or hide the decimal button
    numpad.dec = numpad.target.dataset.decimal==1;
    if (numpad.dec) {
      numpad.zero.classList.remove("zeroN");
      numpad.dot.classList.remove("ninja");
    } else {
      numpad.zero.classList.add("zeroN");
      numpad.dot.classList.add("ninja");
    }

    // Max allowed characters
    numpad.max = parseInt(numpad.target.dataset.max);
    numpad.separator = numpad.target.dataset.separator;
    numpad.input_type = numpad.target.dataset.input_type;

    // Set display value
    var reg = new RegExp('\\' + numpad.separator, 'g');
    var dv = evt.target.value.replace(reg, '');
    if (!isNaN(parseFloat(dv)) && isFinite(dv)) {
      numpad.display.value = evt.target.value;
    } else {
      numpad.display.value = "";
    }

    // Show numpad
    numpad.selector.classList.add("show");
    numpad.display.type = numpad.input_type;
  },

  hide : function () {
  // hide() : hide the number pad

    numpad.selector.classList.remove("show");
  },

  /* [BUTTON ONCLICK ACTIONS] */
  delete : function () {
  // delete() : delete last digit on the number pad

    var length = numpad.display.value.length;
    if (length > 0) {
      if (numpad.display.value[length-2] == numpad.separator){
        numpad.display.value = numpad.display.value.substring(0, length-2);
      }
      else{
        numpad.display.value = numpad.display.value.substring(0, length-1);
      }
    }
  },

  reset : function () {
  // reset() : reset the number pad

    numpad.display.value = "";
  },

  digit : function (evt) {
  // digit() : append a digit
    let reg = new RegExp('\\' + numpad.separator, 'g');
    var current = numpad.display.value.replace(reg, ''),
        append = evt.target.innerHTML;

    if (current.length < numpad.max) {
      if (current=="0") {
        numpad.display.value = append;
      } else {
        let dot_index = numpad.display.value.indexOf(".");
        if (current.length > 0 && dot_index != -1 && (current.length - dot_index) > 2 ){
            return
        }
      if (current.length > 3 && (numpad.separator != 'null') && !(current.length % 4)) {
            numpad.display.value += numpad.separator;
        }
        numpad.display.value += append;
      }
    }
  },

  dot : function () {
  // dot() : add the decimal point (only if not already appended)

    if (numpad.display.value.indexOf(".") == -1) {
      if (numpad.display.value=="") {
        numpad.display.value = "0.";
      } else {
        numpad.display.value += ".";
      }
    }
  },

  select : function () {
  // select() : select the current number

    var value = numpad.display.value;

    // Put selected value to target field + close numpad
    numpad.target.value = value;
    numpad.hide();
  }
};

/* [INIT] */
window.addEventListener("load", numpad.init);