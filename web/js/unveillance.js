String.prototype.escape = function() {
    var tags = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;'
    };
    return this.replace(/[&<>]/g, function(tag) {
        return tags[tag] || tag;
    });
};

function randomString() {
	return Math.random().toString(36).replace(/[^a-z]+/g, '');
}

function getFileContent(ctx, path, callback) {
	var a = $.ajax({
		url: "/files/" + path,
		method: "get",
		complete: callback,
		responseType: "blob",
		context: ctx,
		async: false
	});

	try {
		return a.success().responseText;
	} catch(err) {
		console.error(err);
		return null;
	}
}

function setRawAsset(el, path) {
	$(el).empty();
	$(el).append($(document.createElement('textarea')).html(getFileContent(this, path)));
}

function JSONtoURLString(json) {
	var url_str = Object.keys(json).map(function(key) {
		return (encodeURIComponent(key) + "=" + encodeURIComponent(json[key]));
	}).join('&');
	return url_str;
}

function toggleElement(el) {
	if($(el).css('display') == "block") {
		$(el).css('display','none');
		return false;
	} else {
		$(el).css('display','block');
		return true;
	}
}

function showErrorMessage(el, msg) {
	$(el).html(msg);
	$(el).css('visibility','visible');
}

function validateFormField(field, form_root) {	
	var val = $(field).val();
	
	if($(field).hasClass('uv_mandatory_dz')) {
		val = $(field).html();
	}
	var name = $(field).attr('name');
				
	if($(field).hasClass('uv_mandatory') || $(field).hasClass('uv_mandatory_dz')) {
		if(val == "") {
			$(field).addClass("uv_invalid");
			showErrorMessage($(field).siblings(".uv_error_msg")[0], "Required.");
			return false;
		}
	}
	
	if($(field).hasClass('uv_confirm')) {
		var check_name = name.replace(".confirm", "");
		var check_input = $(form_root).find("input[name='" + check_name + "']")[0];
		
		if(val != $(check_input).val()) {
			$(field).addClass("uv_invalid");
			showErrorMessage(
				$(field).siblings(".uv_error_msg")[0], 
				$(field).attr('uv_error_msg'));
			
			return false;
		}		
	}
	
	return true;
}

function doInnerAjax(url, method, data, callback, async) {
	if(!data) { data = {}}
	if(async === undefined) { async = true; }

	try {
		data._xsrf = $($("input[name='_xsrf']")[0]).val();
	} catch(err) {
		console.error("cannot get xsrf element.");
		console.error(err);
		return null;
	}

	var a = $.ajax({
		url: "/" + url + "/",
		dataType: "json",
		data: data,
		method: method,
		complete: callback,
		async: async,
		error: function(XMLHttpRequest, textStatus, err) {
			console.warn(err);
		}
	});
	
	if(!async) {
		try {
			return JSON.parse(a.success().responseText);
		} catch(err) { console.error(err); }

		return null;
	}
}

function getTemplate(tmpl, on_complete, static_root, ctx) {
	if(!static_root) { static_root = "/web/layout/tmpl/"; }
	if(!ctx) { ctx = this; }
	
	var a_obj = {
		url : (static_root + tmpl),
		method: "get",
		dataType: "html",
		context: ctx,
		async: false
	};
	
	if(on_complete) { a_obj.complete = on_complete; }
	
	var a = $.ajax(a_obj);

	try {
		return a.success().responseText;
	} catch(err) {
		console.error(err);
	}

	return null;
}

function translate(obj) {
	console.info($(obj));

	_.each($(obj).find(".uv_translate"), function(item) {
		var trans = _.filter(UV.TRANSLATE_VALUES, function(t) {
			return _.find($(item).attr('class').split(' '), function(cn) {
				return _.contains(t.keys, cn);
			});
		});

		_.each(trans, function(t) {
			$(item).html(t.enc($(item).html(), $(item)));
		});
	});

	return obj;
}

function insertTemplate(tmpl, data, append_root, on_complete, static_root, ctx) {
	if(data == null) { data = {}; }
	if(!static_root) { static_root = "/web/layout/tmpl/"; }
	
	var a_obj = {
		url : (static_root + tmpl),
		method: "get",
		dataType: "html",
		success: function(html) {
			$(append_root).html(Mustache.to_html(html, data));
			$.each($(append_root).find(".uv_translate"), function(idx, item) {
				if(item.tagName.toLowerCase() == "img" && $(item).attr('repl')) {
					$(item).prop('src', $(item).prop('src').replace($(item).attr('repl'), translate(item)));
				} else {
					$(item).html(translate(item));
				}
			});
		}
	};
	
	if(on_complete) { a_obj.complete = on_complete; }
	if(ctx) { a_obj.context = ctx; }
	
	$.ajax(a_obj);
}

function removeEl(el) {
	$(el).remove();
}

function failOut(el, msg) {
	if(!msg) { msg = "Sorry.  Could not get any results."; }
	$(el).html(msg);
}

function doPost(endpoint, in_el, out_el) {
	if(in_el[0] != "#") {
		in_el = "#" + in_el;
	}
	
	if(out_el[0] != "#") {
		out_el = "#" + out_el;
	}
	
	console.info(endpoint);
	
	data = {}
	
	switch($(in_el).get(0).tagName.toLowerCase()) {
		case "textarea":
			data['input'] = $(in_el).val();
			break;
	}
	
	doInnerAjax(endpoint, "post", data, function(json) {
		console.info(json);
		console.info($(out_el));
		$(out_el).html(JSON.stringify(json));
	});
}

// code via http://dte-project.googlecode.com/svn/trunk/jquery-draggable/index.html
// thank you!
(function($) {
    $.fn.drags = function(opt) {

        opt = $.extend({
            handle: "",
            cursor: "move",
            draggableClass: "draggable",
            activeHandleClass: "active-handle"
        }, opt);

        var $selected = null;
        var $elements = (opt.handle === "") ? this : this.find(opt.handle);

        $elements.css('cursor', opt.cursor).on("mousedown", function(e) {
            if(opt.handle === "") {
                $selected = $(this);
                $selected.addClass(opt.draggableClass);
            } else {
                $selected = $(this).parent();
                $selected.addClass(opt.draggableClass).find(opt.handle).addClass(opt.activeHandleClass);
            }
            var drg_h = $selected.outerHeight(),
                drg_w = $selected.outerWidth(),
                pos_y = $selected.offset().top + drg_h - e.pageY,
                pos_x = $selected.offset().left + drg_w - e.pageX;
            $(document).on("mousemove", function(e) {
                $selected.offset({
                    top: e.pageY + pos_y - drg_h,
                    left: e.pageX + pos_x - drg_w
                });
            }).on("mouseup", function() {
                $(this).off("mousemove"); // Unbind events from document
                if ($selected !== null) {
                    $selected.removeClass(opt.draggableClass);
                    $selected = null;
                }
            });
            e.preventDefault(); // disable selection
        }).on("mouseup", function() {
            if(opt.handle === "") {
                $selected.removeClass(opt.draggableClass);
            } else {
                $selected.removeClass(opt.draggableClass)
                    .find(opt.handle).removeClass(opt.activeHandleClass);
            }
            $selected = null;
        });

        return this;

    };
})(jQuery);