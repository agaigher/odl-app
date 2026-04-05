"""
Client-side JavaScript for the Companies Graph page.

All JS is inlined (no separate static file) so it can reference
the Cytoscape style JSON injected at render time.
"""
from __future__ import annotations

from .cyto import CYTO_STYLE_JSON, CYTO_VAR_MAP_JS

# ---------------------------------------------------------------------------
# Main graph JS (IIFE, injected after Cytoscape CDN loads)
# ---------------------------------------------------------------------------

_GRAPH_JS = r"""
(function () {
  'use strict';

  var cy = null;
  var pathMode = false;
  var pathFrom = null;
  var tooltip = null;
  var focusedNodeId = null;

  var STORAGE_KEY = 'alliela_graph_elements';

  // ── Resolve CSS variables for Cytoscape (canvas cannot read var()) ───────
  var _CYTO_TEMPLATE = __CYTO_STYLE__;
  var _CYTO_VAR_MAP  = __CYTO_VAR_MAP__;

  function resolveCytoStyle() {
    var cs = getComputedStyle(document.documentElement);
    var raw = JSON.stringify(_CYTO_TEMPLATE);
    Object.keys(_CYTO_VAR_MAP).forEach(function (placeholder) {
      var prop = _CYTO_VAR_MAP[placeholder];
      var val  = cs.getPropertyValue(prop).trim() || '';
      // replace all occurrences of the placeholder
      raw = raw.split(placeholder).join(val);
    });
    return JSON.parse(raw);
  }

  function saveGraphToStorage() {
    if (!cy) return;
    try {
      var els = cy.elements().jsons();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(els));
    } catch (e) { /* ignore quota errors */ }
  }

  function loadGraphFromStorage() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function clearGraphStorage() {
    localStorage.removeItem(STORAGE_KEY);
  }

  // ── Tooltip ───────────────────────────────────────────────────────────────
  function createTooltip() {
    tooltip = document.createElement('div');
    tooltip.className = 'graph-tooltip';
    tooltip.style.cssText = 'position:fixed;z-index:999;pointer-events:none;display:none;'
      + 'background:#0a0f1a;color:#fff;font-size:11px;font-family:Inter,sans-serif;'
      + 'padding:6px 10px;border-radius:6px;max-width:220px;line-height:1.4;'
      + 'box-shadow:0 4px 12px rgba(0,0,0,0.3);white-space:pre-wrap;';
    document.body.appendChild(tooltip);
  }

  function showTooltip(evt, node) {
    if (!tooltip) createTooltip();
    var label = node.data('label') || node.data('id');
    var type  = node.data('type') || '';
    var extra = '';
    if (type === 'Company') {
      var status = node.data('status') || node.data('company_status') || '';
      if (status) extra = '\nStatus: ' + status;
    } else if (type === 'Person') {
      var nat = node.data('nationality') || '';
      if (nat) extra = '\nNationality: ' + nat;
      var hubCount = node.data('hub_count');
      if (hubCount) extra += '\nConnects ' + hubCount + ' companies';
    }
    tooltip.textContent = label + extra;
    tooltip.style.display = 'block';
    moveTooltip(evt.originalEvent);
  }

  function moveTooltip(e) {
    if (!tooltip || tooltip.style.display === 'none') return;
    tooltip.style.left = (e.clientX + 14) + 'px';
    tooltip.style.top  = (e.clientY - 10) + 'px';
  }

  function hideTooltip() {
    if (tooltip) tooltip.style.display = 'none';
  }

  // ── Focus / fade ──────────────────────────────────────────────────────────
  function focusNode(node) {
    if (!cy) return;
    focusedNodeId = node.id();
    cy.elements().addClass('faded');
    node.closedNeighborhood().removeClass('faded');
  }

  function clearFocus() {
    if (!cy) return;
    focusedNodeId = null;
    cy.elements().removeClass('faded');
  }

  // ── Layout config ─────────────────────────────────────────────────────────
  var LAYOUT_OPTS = {
    name: 'cose',
    animate: true,
    animationDuration: 500,
    randomize: true,
    nodeRepulsion: 400000,
    nodeOverlap: 40,
    idealEdgeLength: 160,
    edgeElasticity: 200,
    gravity: 25,
    numIter: 1000,
    fit: true,
    padding: 120,
  };

  // ── Sprint 5f: Hub Person Detection ──────────────────────────────────────
  function highlightHubPersons(threshold) {
    if (!cy) return;
    threshold = threshold || 3;
    cy.nodes("[type='Person']").forEach(function (node) {
      var companyNeighbours = node.neighborhood("node[type='Company']").length;
      if (companyNeighbours >= threshold) {
        node.data('hub', 'true');
        node.data('hub_count', companyNeighbours);
      } else {
        node.data('hub', 'false');
        node.removeData('hub_count');
      }
    });
  }

  // ── Sprint 9: Degree-based node sizing ───────────────────────────────────
  function applyDegreeSizing() {
    if (!cy) return;
    cy.nodes().forEach(function (node) {
      var deg = node.degree();
      // clamp sqrt scale: min 50px, max 120px
      var size = Math.min(120, Math.max(50, Math.round(50 + Math.sqrt(deg) * 14)));
      node.style({ width: size + 'px', height: size + 'px' });
    });
  }

  // ── Sprint 9: Edge thickness by pair frequency ───────────────────────────
  function applyEdgeThickness() {
    if (!cy) return;
    var pairCounts = {};
    cy.edges().forEach(function (edge) {
      var key = [edge.data('source'), edge.data('target')].sort().join('||');
      pairCounts[key] = (pairCounts[key] || 0) + 1;
    });
    cy.edges().forEach(function (edge) {
      var key = [edge.data('source'), edge.data('target')].sort().join('||');
      var count = pairCounts[key] || 1;
      // scale 1.5px → 4px based on count, capped at 8
      var w = Math.min(4, 1.5 + (count - 1) * 0.5);
      edge.style({ width: w });
    });
  }

  // ── Sprint 9: Dark mode graph skin ───────────────────────────────────────
  function applyCytoTheme(dark) {
    if (!cy) return;
    cy.style(resolveCytoStyle());
    applyDegreeSizing();
    applyEdgeThickness();
  }
  window.applyCytoTheme = applyCytoTheme;

  // ── Initialise or re-use Cytoscape instance ───────────────────────────────
  function initCy(elements) {
    if (cy) return;
    createTooltip();
    var initElements = elements;
    if (!initElements || !initElements.length) {
      var stored = loadGraphFromStorage();
      if (stored && stored.length) initElements = stored;
    }
    cy = cytoscape({
      container: document.getElementById('cy'),
      elements: initElements || [],
      style: resolveCytoStyle(),
      layout: initElements && initElements.length
        ? Object.assign({}, LAYOUT_OPTS, { animate: false })
        : LAYOUT_OPTS,
      userZoomingEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.1,
      maxZoom: 4,
    });

    cy.on('layoutstop', function () {
      highlightHubPersons();
      applyDegreeSizing();
      applyEdgeThickness();
    });

    cy.on('tap', 'node', function (evt) {
      var node = evt.target;
      var rawId = node.data('raw_id') || node.data('id');
      var type  = node.data('type');

      if (pathMode) {
        if (!pathFrom) {
          pathFrom = { id: rawId, type: type };
          node.addClass('highlighted');
          return;
        }
        if (pathFrom.id !== rawId) {
          fetchPath(pathFrom, { id: rawId, type: type });
        }
        cy.nodes().removeClass('highlighted');
        pathFrom = null;
        return;
      }

      focusNode(node);
      fetchDetail(type, rawId);
    });

    cy.on('tap', function (evt) {
      if (evt.target !== cy) return;
      clearFocus();
      document.getElementById('graph-sidebar-content').innerHTML =
        '<p class="graph-sidebar__placeholder">Click a node to see details</p>';
    });

    cy.on('dbltap', 'node', function (evt) {
      hideTooltip();
      var node = evt.target;
      var rawId = node.data('raw_id') || node.data('id');
      var type  = node.data('type');
      triggerExpand(type, rawId, getGlobalDepth());
    });

    cy.on('mouseover', 'node', function (evt) {
      showTooltip(evt, evt.target);
      evt.target.addClass('hovered');
    });
    cy.on('mousemove', 'node', function (evt) { moveTooltip(evt.originalEvent); });
    cy.on('mouseout',  'node', function (evt) {
      hideTooltip();
      evt.target.removeClass('hovered');
    });

    document.getElementById('cy').addEventListener('mousemove', moveTooltip);

    // Run hub detection and sizing on init
    highlightHubPersons();
    applyDegreeSizing();
    applyEdgeThickness();
    // Apply current theme skin
    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDark) cy.style(resolveCytoStyle());
  }

  // ── Merge new elements without duplicates ─────────────────────────────────
  function mergeElements(newEls) {
    if (!newEls || !newEls.length) return;
    if (!cy) {
      initCy(newEls);
      saveGraphToStorage();
      return;
    }
    var added = [];
    newEls.forEach(function (el) {
      if (!cy.getElementById(el.data.id).length) {
        cy.add(el);
        added.push(el.data.id);
      }
    });
    if (added.length) {
      clearFocus();
      cy.layout(Object.assign({}, LAYOUT_OPTS, { fit: false })).run();
      saveGraphToStorage();
    }
    highlightHubPersons();
    applyDegreeSizing();
    applyEdgeThickness();
  }

  // ── Global depth ──────────────────────────────────────────────────────────
  function getGlobalDepth() {
    var el = document.getElementById('global-depth-slider');
    return el ? parseInt(el.value, 10) || 1 : 1;
  }

  // ── Fetch entity detail into sidebar ──────────────────────────────────────
  function fetchDetail(type, id) {
    var url = '/companies-graph/entity/' + encodeURIComponent(type) + '/' + encodeURIComponent(id);
    var sidebar = document.getElementById('graph-sidebar');
    if (sidebar) sidebar.style.width = '260px';
    document.getElementById('graph-sidebar-content').innerHTML =
      '<p class="graph-sidebar__placeholder">Loading\u2026</p>';
    fetch(url, { headers: { 'HX-Request': 'true' } })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        document.getElementById('graph-sidebar-content').innerHTML = html;
        var slider = document.getElementById('sidebar-depth-slider');
        var label  = document.getElementById('sidebar-depth-label');
        if (slider && label) {
          slider.addEventListener('input', function () { label.textContent = this.value; });
        }
        var btn = document.getElementById('sidebar-expand-btn');
        if (btn) {
          btn.addEventListener('click', function () {
            triggerExpand(btn.dataset.nodeType, btn.dataset.nodeId, getGlobalDepth());
          });
        }
      })
      .catch(function () {
        document.getElementById('graph-sidebar-content').innerHTML =
          '<p class="graph-sidebar__placeholder">Could not load details.</p>';
      });
  }

  // ── Trigger expand ────────────────────────────────────────────────────────
  function triggerExpand(type, id, depth) {
    fetch('/companies-graph/expand/' + encodeURIComponent(id), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'HX-Request': 'true' },
      body: 'node_type=' + encodeURIComponent(type) + '&depth=' + (depth || 1),
    })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var payload = tmp.querySelector('#graph-data-payload');
        if (payload) {
          try { mergeElements(JSON.parse(payload.textContent)); } catch (e) {}
        }
      });
  }

  // ── Full CH Enrichment ────────────────────────────────────────────────────
  function startEnrichment(entityType, entityId) {
    var sidebar = document.getElementById('graph-sidebar');
    if (sidebar) sidebar.style.width = Math.floor(window.innerWidth * 0.5) + 'px';
    var btn = document.getElementById('sidebar-enrich-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Enriching\u2026'; }
    fetch('/companies-graph/enrich/' + encodeURIComponent(entityType) + '/' + encodeURIComponent(entityId), {
      method: 'POST',
      headers: { 'HX-Request': 'true' },
    })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var panel = document.getElementById('enrichment-panel');
        if (panel) { panel.outerHTML = html; }
        if (typeof htmx !== 'undefined') {
          var newPanel = document.getElementById('enrichment-panel');
          if (newPanel) htmx.process(newPanel);
        }
      })
      .catch(function () {
        var panel = document.getElementById('enrichment-panel');
        if (panel) panel.innerHTML = '<p class="enrich-error">Failed to start enrichment.</p>';
        if (btn) { btn.disabled = false; btn.textContent = '\u26a1 Full CH Enrichment'; }
      });
  }

  function showEnrichTab(slug) {
    document.querySelectorAll('.enrich-tab__pane').forEach(function (p) {
      p.classList.remove('enrich-tab__pane--active');
    });
    document.querySelectorAll('.enrich-tab__btn').forEach(function (b) {
      b.classList.remove('enrich-tab__btn--active');
    });
    var pane = document.getElementById('enrich-tab-' + slug);
    if (pane) pane.classList.add('enrich-tab__pane--active');
    var btn = document.getElementById('enrich-tab-btn-' + slug);
    if (btn) btn.classList.add('enrich-tab__btn--active');
  }

  function setEnrichedNode(nodeId) {
    if (!cy || !nodeId) return;
    var node = cy.getElementById(nodeId);
    if (node && node.length) {
      node.data('enriched', 'true');
      saveGraphToStorage();
    }
  }

  // Apply risk level to a node after entity detail fetch
  function applyRiskLevel(cytoNodeId, riskLevel) {
    if (!cy || !cytoNodeId || !riskLevel) return;
    var node = cy.getElementById(cytoNodeId);
    if (node && node.length) {
      node.data('risk_level', riskLevel);
      saveGraphToStorage();
    }
  }

  function addOfficerCompaniesToGraph(companyNumbers) {
    if (!companyNumbers || !companyNumbers.length) return;
    var body = companyNumbers.map(function (n) {
      return 'node=' + encodeURIComponent(JSON.stringify({ kind: 'company', id: n }));
    }).join('&');
    fetch('/companies-graph/add-nodes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'HX-Request': 'true' },
      body: body,
    })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var payload = tmp.querySelector('#graph-data-payload');
        if (payload) {
          try { mergeElements(JSON.parse(payload.textContent)); } catch (e) {}
        }
      });
  }

  // ── Fetch shortest path ───────────────────────────────────────────────────
  function fetchPath(from, to) {
    var url = '/companies-graph/path'
      + '?from_id='   + encodeURIComponent(from.id)
      + '&from_type=' + encodeURIComponent(from.type)
      + '&to_id='     + encodeURIComponent(to.id)
      + '&to_type='   + encodeURIComponent(to.type);
    fetch(url, { headers: { 'HX-Request': 'true' } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.elements) mergeElements(data.elements);
        if (data.path_ids) highlightPath(data.path_ids);
      });
  }

  function highlightPath(ids) {
    cy.elements().removeClass('highlighted');
    ids.forEach(function (id) { cy.getElementById(id).addClass('highlighted'); });
  }

  // ── HTMX afterSwap ────────────────────────────────────────────────────────
  document.body.addEventListener('htmx:afterSwap', function (evt) {
    var dataEl = document.getElementById('graph-data-payload');
    if (dataEl) {
      try { mergeElements(JSON.parse(dataEl.textContent)); } catch (e) {}
      dataEl.remove();
    }

    var incoming = document.getElementById('search-results-incoming');
    if (!incoming || !incoming.children.length) return;
    var newItems = incoming.querySelectorAll('.search-result__item');
    if (!newItems.length) return;

    var container = document.getElementById('search-results-items');
    newItems.forEach(function (item) {
      var kind = item.dataset.kind || '';
      var id   = item.dataset.id   || '';
      if (container.querySelector('[data-kind="' + kind + '"][data-id="' + id + '"]')) return;
      var clone = item.cloneNode(true);
      clone.dataset.checked = 'false';
      container.appendChild(clone);
    });
    incoming.innerHTML = '';
    updateSelectionState();
    updateResultsCount();
  });

  // ── Search results ────────────────────────────────────────────────────────
  function toggleSearchResultItem(el) {
    var checked = el.dataset.checked === 'true';
    el.dataset.checked = checked ? 'false' : 'true';
    el.classList.toggle('search-result__item--selected', !checked);
    updateSelectionState();
  }
  window.toggleSearchResultItem = toggleSearchResultItem;

  function updateSelectionState() {
    var selected = document.querySelectorAll('#search-results-items .search-result__item[data-checked="true"]');
    var count = selected.length;
    var btn = document.getElementById('btn-add-to-graph');
    var label = document.getElementById('selection-count-label');
    var section = document.getElementById('add-to-graph-section');
    var clearBtn = document.getElementById('btn-clear-selection');
    var hasItems = document.getElementById('search-results-items').children.length > 0;
    if (btn) btn.disabled = count === 0;
    if (label) label.textContent = count + ' selected';
    if (section) section.style.display = hasItems ? '' : 'none';
    if (clearBtn) clearBtn.style.display = count > 0 ? '' : 'none';
  }

  function updateResultsCount() {
    var items = document.querySelectorAll('#search-results-items .search-result__item');
    var header = document.getElementById('search-results-header');
    var countEl = document.getElementById('search-results-count');
    if (header) header.style.display = items.length ? '' : 'none';
    if (countEl) countEl.textContent = items.length + ' result' + (items.length !== 1 ? 's' : '');
  }

  document.getElementById('btn-clear-search').addEventListener('click', function () {
    document.getElementById('graph-search-input').value = '';
    document.getElementById('search-results-items').innerHTML = '';
    document.getElementById('search-results-incoming').innerHTML = '';
    updateSelectionState();
    updateResultsCount();
  });

  document.getElementById('btn-clear-selection').addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelectorAll('#search-results-items .search-result__item').forEach(function (item) {
      item.dataset.checked = 'false';
      item.classList.remove('search-result__item--selected');
    });
    updateSelectionState();
  });

  document.getElementById('btn-add-to-graph').addEventListener('click', function () {
    var selected = document.querySelectorAll('#search-results-items .search-result__item[data-checked="true"]');
    if (!selected.length) return;
    var body = [];
    selected.forEach(function (item) {
      var cbData = item.querySelector('.search-result__cb-data');
      if (cbData && cbData.dataset.cbValue) {
        body.push('node=' + encodeURIComponent(cbData.dataset.cbValue));
      }
    });
    if (!body.length) return;
    var btn = this;
    btn.disabled = true;
    btn.textContent = 'Adding...';
    fetch('/companies-graph/add-nodes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'HX-Request': 'true' },
      body: body.join('&'),
    })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var payload = tmp.querySelector('#graph-data-payload');
        if (payload) {
          try { mergeElements(JSON.parse(payload.textContent)); } catch (e) {}
        }
        selected.forEach(function (item) {
          item.dataset.checked = 'false';
          item.classList.remove('search-result__item--selected');
        });
        updateSelectionState();
      })
      .finally(function () {
        btn.disabled = false;
        btn.textContent = 'Add to Graph';
      });
  });

  // ── Toolbar ───────────────────────────────────────────────────────────────
  document.getElementById('btn-path-mode').addEventListener('click', function () {
    pathMode = !pathMode;
    pathFrom = null;
    if (cy) cy.nodes().removeClass('highlighted');
    this.classList.toggle('graph-nav__btn--active', pathMode);
    document.getElementById('path-hint').style.display = pathMode ? 'inline' : 'none';
  });

  document.getElementById('btn-fit').addEventListener('click', function () {
    if (cy) cy.fit(undefined, 120);
  });

  document.getElementById('btn-zoom-in').addEventListener('click', function () {
    if (!cy) return;
    cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  });
  document.getElementById('btn-zoom-out').addEventListener('click', function () {
    if (!cy) return;
    cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  });

  document.getElementById('color-bg').addEventListener('input', function () {
    var el = document.getElementById('cy');
    if (el) el.style.backgroundColor = this.value;
  });
  document.getElementById('color-company').addEventListener('input', function () {
    if (!cy) return;
    cy.style().selector("node[type='Company']").style('background-color', this.value).update();
  });
  document.getElementById('color-person').addEventListener('input', function () {
    if (!cy) return;
    cy.style().selector("node[type='Person']").style('background-color', this.value).update();
  });

  (function () {
    var slider = document.getElementById('global-depth-slider');
    var label  = document.getElementById('global-depth-label');
    if (!slider || !label) return;
    slider.addEventListener('input', function () { label.textContent = this.value; });
    slider.addEventListener('change', function () {
      if (!cy) return;
      var depth = parseInt(this.value, 10);
      cy.nodes().forEach(function (node) {
        var type = node.data('type');
        var rawId = node.data('raw_id') || node.data('id');
        if (type === 'Company' || type === 'Person') {
          triggerExpand(type, rawId, depth);
        }
      });
    });
  })();

  // ── Filter dropdowns ──────────────────────────────────────────────────────
  function applyGraphFilters() {
    if (!cy) return;
    var visibleNodeTypes = {};
    document.querySelectorAll('.graph-filter-node').forEach(function (cb) {
      visibleNodeTypes[cb.dataset.type] = cb.checked;
    });
    var visibleRelTypes = {};
    document.querySelectorAll('.graph-filter-rel').forEach(function (cb) {
      visibleRelTypes[cb.dataset.type] = cb.checked;
    });
    cy.nodes().forEach(function (n) {
      n.style('display', visibleNodeTypes[n.data('type')] !== false ? 'element' : 'none');
    });
    cy.edges().forEach(function (e) {
      var relType = (e.data('label') || e.data('type') || '').toUpperCase();
      var relVisible = visibleRelTypes[relType] !== false;
      var srcHidden = e.source().style('display') === 'none';
      var tgtHidden = e.target().style('display') === 'none';
      e.style('display', (relVisible && !srcHidden && !tgtHidden) ? 'element' : 'none');
    });
  }

  ['nodes', 'rels'].forEach(function (prefix) {
    var trigger = document.getElementById(prefix + '-dropdown-trigger');
    var menu = document.getElementById(prefix + '-dropdown-menu');
    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = menu.classList.toggle('graph-nav__dropdown-menu--open');
      trigger.classList.toggle('graph-nav__btn--active', isOpen);
      var other = prefix === 'nodes' ? 'rels' : 'nodes';
      document.getElementById(other + '-dropdown-menu').classList.remove('graph-nav__dropdown-menu--open');
      document.getElementById(other + '-dropdown-trigger').classList.remove('graph-nav__btn--active');
    });
  });
  document.addEventListener('click', function () {
    document.querySelectorAll('.graph-nav__dropdown-menu').forEach(function (m) {
      m.classList.remove('graph-nav__dropdown-menu--open');
    });
    document.querySelectorAll('.graph-nav__dropdown-trigger').forEach(function (t) {
      t.classList.remove('graph-nav__btn--active');
    });
  });
  document.querySelectorAll('.graph-nav__dropdown-menu').forEach(function (m) {
    m.addEventListener('click', function (e) { e.stopPropagation(); });
  });

  document.querySelector('.graph-filter-node-all').addEventListener('change', function () {
    var checked = this.checked;
    document.querySelectorAll('.graph-filter-node').forEach(function (cb) { cb.checked = checked; });
    applyGraphFilters();
  });
  document.querySelectorAll('.graph-filter-node').forEach(function (cb) {
    cb.addEventListener('change', function () {
      var all = Array.from(document.querySelectorAll('.graph-filter-node')).every(function (c) { return c.checked; });
      document.querySelector('.graph-filter-node-all').checked = all;
      applyGraphFilters();
    });
  });

  document.querySelector('.graph-filter-rel-all').addEventListener('change', function () {
    var checked = this.checked;
    document.querySelectorAll('.graph-filter-rel').forEach(function (cb) { cb.checked = checked; });
    applyGraphFilters();
  });
  document.querySelectorAll('.graph-filter-rel').forEach(function (cb) {
    cb.addEventListener('change', function () {
      var all = Array.from(document.querySelectorAll('.graph-filter-rel')).every(function (c) { return c.checked; });
      document.querySelector('.graph-filter-rel-all').checked = all;
      applyGraphFilters();
    });
  });

  // ── Clear graph ───────────────────────────────────────────────────────────
  document.getElementById('btn-graph-clear').addEventListener('click', function () {
    clearGraphStorage();
    if (cy) { cy.destroy(); cy = null; }
    pathMode = false;
    pathFrom = null;
    focusedNodeId = null;
    document.getElementById('graph-sidebar-content').innerHTML =
      '<p class="graph-sidebar__placeholder">Click a node to see details</p>';
    document.getElementById('btn-path-mode').classList.remove('graph-nav__btn--active');
    document.getElementById('path-hint').style.display = 'none';
  });

  // ── Restore from localStorage ─────────────────────────────────────────────
  var storedEls = loadGraphFromStorage();
  if (storedEls && storedEls.length) {
    function tryRestore() {
      if (typeof cytoscape === 'undefined') { setTimeout(tryRestore, 50); return; }
      initCy(null);
    }
    tryRestore();
  }

  // ── Left panel resize ─────────────────────────────────────────────────────
  (function () {
    var handle = document.getElementById('left-panel-resize-handle');
    var panel  = handle && handle.closest('.graph-left-panel');
    if (!handle || !panel) return;
    var startX, startW;
    handle.addEventListener('mousedown', function (e) {
      e.preventDefault();
      startX = e.clientX;
      startW = panel.offsetWidth;
      handle.classList.add('graph-left-panel__resize-handle--dragging');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      function onMove(e) {
        var delta = e.clientX - startX;
        var minW  = parseInt(getComputedStyle(panel).minWidth) || 200;
        var maxW  = parseInt(getComputedStyle(panel).maxWidth) || 520;
        panel.style.width = Math.min(maxW, Math.max(minW, startW + delta)) + 'px';
      }
      function onUp() {
        handle.classList.remove('graph-left-panel__resize-handle--dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  })();

  // ── Right sidebar resize ──────────────────────────────────────────────────
  (function () {
    var handle = document.getElementById('sidebar-resize-handle');
    var panel  = handle && handle.closest('.graph-sidebar');
    if (!handle || !panel) return;
    var startX, startW;
    handle.addEventListener('mousedown', function (e) {
      e.preventDefault();
      startX = e.clientX;
      startW = panel.offsetWidth;
      handle.classList.add('graph-sidebar__resize-handle--dragging');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      function onMove(e) {
        var delta = startX - e.clientX;
        var minW  = parseInt(getComputedStyle(panel).minWidth) || 200;
        panel.style.width = Math.max(minW, startW + delta) + 'px';
      }
      function onUp() {
        handle.classList.remove('graph-sidebar__resize-handle--dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  })();

  // Expose globals needed by inline onclick= handlers
  window.fetchDetail       = fetchDetail;
  window.startEnrichment   = startEnrichment;
  window.showEnrichTab     = showEnrichTab;
  window.setEnrichedNode   = setEnrichedNode;
  window.applyRiskLevel    = applyRiskLevel;
  window.mergeElements     = mergeElements;
  window.addOfficerCompaniesToGraph = addOfficerCompaniesToGraph;

  function addOwnerToGraph(companyNumber, companyName) {
    var body = 'node=' + encodeURIComponent(JSON.stringify({ kind: 'company', id: companyNumber }));
    fetch('/companies-graph/add-nodes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'HX-Request': 'true' },
      body: body,
    })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var payload = tmp.querySelector('#graph-data-payload');
        if (payload) {
          try { mergeElements(JSON.parse(payload.textContent)); } catch (e) {}
        }
      });
  }
  window.addOwnerToGraph = addOwnerToGraph;

})();
"""


def build_js() -> str:
    js = _GRAPH_JS.replace("__CYTO_STYLE__", CYTO_STYLE_JSON)
    js = js.replace("__CYTO_VAR_MAP__", CYTO_VAR_MAP_JS)
    return js
