/* PsyClawForms — self-contained form engine for psyclaw-webui.
 *
 * Responsibilities:
 *   - bindForm(form)        : attach input/change listeners (idempotent)
 *   - readForm(form)        : walk named fields -> spec dict
 *   - showPreview(form, c)  : render spec dict as JSON in a container
 *   - validate(form)        : check required / min / max; mark invalid fields
 *
 * Dispatches document-level custom event:
 *   document.addEventListener('psyclaw:formchange', e => e.detail === specDict)
 *
 * Supports data-attributes on field containers:
 *   data-show-when="field=value"  : show only when referenced field equals value
 *   data-required="true"          : must be non-empty (numbers must parse)
 *   data-min / data-max           : numeric range (on number inputs)
 *   data-paradigm="<name>"        : on the form root; becomes spec.paradigm
 *
 * Exposes:
 *   window.PsyClawForms = { bindForm, readForm, showPreview, validate }
 */
(function () {
  'use strict';

  // Track forms we've already bound to prevent double-attaching listeners.
  var boundForms = new WeakSet();

  // Internal: list of input selectors that carry a `name` attribute.
  var FIELD_SELECTOR = 'input[name], textarea[name], select[name]';

  // -- helpers --------------------------------------------------------------

  function $(form, sel) {
    return form.querySelector(sel);
  }

  function $$(form, sel) {
    return Array.prototype.slice.call(form.querySelectorAll(sel));
  }

  // Order fields by their position in the DOM (document order).
  function orderedFields(form) {
    return $$(form, FIELD_SELECTOR);
  }

  // Coerce a single input/textarea/select value to a JS value.
  function coerceValue(el) {
    var tag = el.tagName.toLowerCase();
    var type = (el.getAttribute('type') || '').toLowerCase();

    if (tag === 'input' && type === 'checkbox') {
      return !!el.checked;
    }
    if (tag === 'input' && (type === 'number' || type === 'range')) {
      var raw = el.value;
      if (raw === '' || raw === null || raw === undefined) return null;
      var n = Number(raw);
      return isNaN(n) ? null : n;
    }
    if (tag === 'input' && type === 'color') {
      return el.value || '';
    }
    if (tag === 'select') {
      // Use the selected option's value (or text as fallback).
      var opt = el.options[el.selectedIndex];
      return opt ? opt.value : '';
    }
    // text, textarea, hidden, date, etc. — keep as string.
    return el.value;
  }

  // Apply visibility rules declared via data-show-when on field containers.
  // A rule like data-show-when="paradigm=stroop" hides the container
  // (the <label class="field"> wrapper) unless the named field equals value.
  function applyVisibility(form) {
    var spec = readFormRaw(form);
    var containers = $$(form, '[data-show-when]');
    containers.forEach(function (el) {
      var rule = el.getAttribute('data-show-when') || '';
      var eq = rule.indexOf('=');
      if (eq < 0) return;
      var field = rule.slice(0, eq).trim();
      var value = rule.slice(eq + 1).trim();
      var current = spec[field];
      // Loose comparison: numbers vs strings, booleans.
      var match = String(current) === value;
      el.style.display = match ? '' : 'none';
    });
  }

  // Read a field's value WITHOUT triggering formchange (used by visibility).
  function readFormRaw(form) {
    var out = {};
    var paradigm = form.getAttribute('data-paradigm');
    if (paradigm) out.paradigm = paradigm;
    orderedFields(form).forEach(function (el) {
      if (!el.name) return;
      var v = coerceValue(el);
      if (v === null) return; // skip empty number fields
      out[el.name] = v;
    });
    return out;
  }

  // -- public API ------------------------------------------------------------

  // Build a <label class="field"> wrapper + inner input from a FieldSpec.
  // Used by the UI shell to materialize a form from the paradigm schema.
  function buildField(schemaField) {
    var wrap = document.createElement('label');
    wrap.className = 'field';
    if (schemaField.required) wrap.dataset.required = 'true';

    var label = document.createElement('span');
    label.textContent = schemaField.label || schemaField.name;
    wrap.appendChild(label);

    var input;
    var type = schemaField.type || 'text';

    if (type === 'textarea') {
      input = document.createElement('textarea');
      input.rows = 3;
    } else if (type === 'checkbox') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = schemaField.default === true;
      wrap.appendChild(input);
      // No need for inner label for checkbox
      return wrap;
    } else if (type === 'select') {
      input = document.createElement('select');
      (schemaField.options || []).forEach(function (opt) {
        var o = document.createElement('option');
        o.value = String(opt);
        o.textContent = String(opt);
        if (opt === schemaField.default) o.selected = true;
        input.appendChild(o);
      });
    } else if (type === 'multiselect') {
      input = document.createElement('select');
      input.multiple = true;
      (schemaField.options || []).forEach(function (opt) {
        var o = document.createElement('option');
        o.value = String(opt);
        o.textContent = String(opt);
        input.appendChild(o);
      });
    } else if (type === 'color') {
      input = document.createElement('input');
      input.type = 'color';
      if (schemaField.default) input.value = schemaField.default;
    } else if (type === 'slider') {
      input = document.createElement('input');
      input.type = 'range';
      if (schemaField.min !== undefined) input.min = schemaField.min;
      if (schemaField.max !== undefined) input.max = schemaField.max;
      if (schemaField.default !== undefined) input.value = schemaField.default;
    } else if (type === 'number') {
      input = document.createElement('input');
      input.type = 'number';
      if (schemaField.default !== undefined) input.value = schemaField.default;
      if (schemaField.min !== undefined) input.min = schemaField.min;
      if (schemaField.max !== undefined) input.max = schemaField.max;
    } else {
      // text (default)
      input = document.createElement('input');
      input.type = 'text';
      if (schemaField.default !== undefined) input.value = schemaField.default;
    }

    input.name = schemaField.name;
    if (schemaField.required) input.required = true;
    wrap.appendChild(input);
    return wrap;
  }

  // Build a complete form (returns a <form> element with all fields wired up).
  function renderForm(schemaFields, paradigmId) {
    var form = document.createElement('form');
    form.className = 'form';
    if (paradigmId) form.dataset.paradigm = paradigmId;
    schemaFields.forEach(function (f) {
      form.appendChild(buildField(f));
    });
    bindForm(form);
    return form;
  }

  function readForm(form) {
    return readFormRaw(form);
  }

  function showPreview(form, container) {
    if (!container) return;
    var spec = readFormRaw(form);
    try {
      container.textContent = JSON.stringify(spec, null, 2);
    } catch (e) {
      container.textContent = '[PsyClawForms] could not serialize spec: ' + e.message;
    }
  }

  function validate(form) {
    var errors = [];
    var fields = orderedFields(form);

    fields.forEach(function (el) {
      // Strip any prior invalid marker.
      el.classList.remove('invalid');
      var marker = el.parentNode && el.parentNode.querySelector('.psyclaw-error-mark');
      if (marker) marker.remove();

      var required = el.getAttribute('data-required') === 'true' ||
                     (el.hasAttribute('required'));
      if (!required) return;

      var tag = el.tagName.toLowerCase();
      var type = (el.getAttribute('type') || '').toLowerCase();
      var name = el.name;

      if (tag === 'input' && type === 'checkbox') {
        // For checkboxes, "required" usually means must be checked.
        if (!el.checked) {
          errors.push({ field: name, msg: 'Must be checked' });
          markInvalid(el);
        }
        return;
      }

      if (tag === 'input' && (type === 'number' || type === 'range')) {
        var raw = el.value;
        if (raw === '' || raw === null) {
          errors.push({ field: name, msg: 'Required' });
          markInvalid(el);
          return;
        }
        var n = Number(raw);
        if (isNaN(n)) {
          errors.push({ field: name, msg: 'Not a number' });
          markInvalid(el);
          return;
        }
        if (el.hasAttribute('data-min') && n < Number(el.getAttribute('data-min'))) {
          errors.push({ field: name, msg: 'Min ' + el.getAttribute('data-min') });
          markInvalid(el);
        }
        if (el.hasAttribute('data-max') && n > Number(el.getAttribute('data-max'))) {
          errors.push({ field: name, msg: 'Max ' + el.getAttribute('data-max') });
          markInvalid(el);
        }
        return;
      }

      // text / textarea / select — must be non-empty
      var v = (el.value || '').trim();
      if (v === '') {
        errors.push({ field: name, msg: 'Required' });
        markInvalid(el);
      }
    });

    return { valid: errors.length === 0, errors: errors };
  }

  function markInvalid(el) {
    el.classList.add('invalid');
    // Add a small red marker after the field (within its parent <label.field>).
    var parent = el.parentNode;
    if (parent && !parent.querySelector('.psyclaw-error-mark')) {
      var m = document.createElement('span');
      m.className = 'psyclaw-error-mark';
      m.textContent = ' *';
      m.style.color = '#c44e52';
      m.style.fontWeight = 'bold';
      m.style.marginLeft = '4px';
      parent.appendChild(m);
    }
  }

  function bindForm(form) {
    if (!form || !(form instanceof HTMLElement)) return;
    if (boundForms.has(form)) return; // already bound
    boundForms.add(form);

    // Single delegated listener — fires for any input change in the form.
    form.addEventListener('input', onChange);
    form.addEventListener('change', onChange);

    // React to outside updates (e.g. paradigm switch triggers refresh).
    // We refresh both the spec-preview-json pane and any caller-passed
    // container (handled directly by showPreview() invocations).
    document.addEventListener('psyclaw:formchange', function (e) {
      if (e && e.detail && e.detail.__form === form) {
        var pane = document.getElementById('spec-preview-json');
        if (pane) showPreview(form, pane);
      }
    });

    // Initial pass: hide/show conditional fields, then fire one change event
    // so downstream code can pick up the initial spec.
    applyVisibility(form);
    fireChange(form);
  }

  function onChange(ev) {
    var form = ev.currentTarget;
    applyVisibility(form);
    fireChange(form);
  }

  function fireChange(form) {
    var spec = readFormRaw(form);
    spec.__form = form; // identity for the listener above
    document.dispatchEvent(new CustomEvent('psyclaw:formchange', { detail: spec }));
  }

  // Expose
  window.PsyClawForms = {
    bindForm: bindForm,
    readForm: readForm,
    showPreview: showPreview,
    validate: validate,
    buildField: buildField,
    renderForm: renderForm,
    // expose for testing / advanced use
    _applyVisibility: applyVisibility,
    _readFormRaw: readFormRaw,
  };
})();
