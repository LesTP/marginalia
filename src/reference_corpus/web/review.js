"use strict";

const dataNode = document.getElementById("corpus-data");
const corpusData = JSON.parse(dataNode.textContent);
const readableAnnotations = corpusData.annotations.filter((annotation) => !annotation.is_base_text);
const annotationsByKey = new Map(readableAnnotations.map((annotation) => [annotation.local_key, annotation]));
const lensesById = new Map(corpusData.presentation.lenses.map((lens) => [lens.id, lens]));
const pathwaysById = new Map(corpusData.presentation.pathways.map((pathway) => [pathway.id, pathway]));
const textViews = corpusData.texts || [{
  id: "canonical",
  label: "Base text",
  type: "canonical-target",
  provenance_note: `Base witness: ${corpusData.corpus.base_witness.citation}`,
  lines: corpusData.poem.lines,
}];
const textsById = new Map(textViews.map((text) => [text.id, text]));
const hasMultipleTexts = textViews.length > 1;

const elements = {
  title: document.getElementById("edition-title"),
  author: document.getElementById("edition-author"),
  status: document.getElementById("edition-status"),
  shell: document.querySelector(".edition-shell"),
  readingNav: document.getElementById("reading-nav"),
  modeDescription: document.getElementById("mode-description"),
  textSelector: document.getElementById("text-view-selector"),
  witnessPresentation: document.getElementById("witness-presentation"),
  witnessCredit: document.getElementById("witness-credit"),
  witnessHeading: document.getElementById("witness-heading"),
  poem: document.getElementById("poem-lines"),
  witness: document.getElementById("base-witness"),
  readingPanel: document.getElementById("reading-detail"),
  readingGrid: document.getElementById("reading-grid"),
  annotationCollection: document.getElementById("annotation-collection"),
  sourceDetail: document.getElementById("source-detail"),
  sourceList: document.getElementById("source-list"),
  pathwayDetail: document.getElementById("pathway-detail"),
  description: document.getElementById("corpus-description"),
};

function makeElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined && text !== null) {
    node.textContent = text;
  }
  return node;
}

function humanize(value) {
  return value.replaceAll("_", " ").replaceAll("-", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function metadataLine(label, value) {
  const paragraph = makeElement("p", "source-meta");
  paragraph.append(makeElement("strong", null, `${label}: `), document.createTextNode(value));
  return paragraph;
}

function appendBadge(container, value, modifier) {
  const badge = makeElement("span", `badge${modifier ? ` badge--${modifier}` : ""}`, humanize(value));
  container.append(badge);
}

function modeItems() {
  return [
    {
      kind: "plain",
      id: "plain",
      label: "Plain reading",
      description: "Read the base text without an active annotation.",
    },
    ...corpusData.presentation.pathways.map((pathway) => ({kind: "pathway", ...pathway})),
    ...corpusData.presentation.lenses.map((lens) => ({kind: "lens", ...lens})),
    {
      kind: "all",
      id: "all",
      label: "All notes",
      description: "Browse every annotation in manifest order.",
    },
    {
      kind: "sources",
      id: "sources",
      label: "Sources",
      description: "Review bibliography, access state, authority, and rights information.",
    },
  ];
}

function activeModeItem() {
  if (state.mode === "lens") {
    return modeItems().find((item) => item.kind === "lens" && item.id === state.lens);
  }
  if (state.mode === "pathway") {
    return modeItems().find((item) => item.kind === "pathway" && item.id === state.pathway);
  }
  return modeItems().find((item) => item.kind === state.mode);
}

function annotationKeysForState(candidate) {
  if (candidate.mode === "lens") {
    return lensesById.get(candidate.lens)?.annotation_keys || [];
  }
  if (candidate.mode === "pathway") {
    const pathway = pathwaysById.get(candidate.pathway);
    if (!pathway) {
      return [];
    }
    return pathway.steps.find((step) => step.id === candidate.step)?.annotation_keys || [];
  }
  if (candidate.mode === "all") {
    return readableAnnotations.map((annotation) => annotation.local_key);
  }
  return [];
}

function normalizedState(candidate) {
  const next = {
    text: textsById.has(candidate.text) ? candidate.text : corpusData.presentation.default_text,
    mode: candidate.mode,
    lens: candidate.lens || null,
    pathway: candidate.pathway || null,
    step: candidate.step || null,
    annotation: candidate.annotation || null,
    specificNote: candidate.specificNote === true,
  };
  if (["plain", "sources"].includes(next.mode)) {
    next.lens = null;
    next.pathway = null;
    next.step = null;
    next.annotation = null;
    next.specificNote = false;
    return next;
  }
  if (next.mode === "lens") {
    if (!lensesById.has(next.lens)) {
      return null;
    }
    next.pathway = null;
    next.step = null;
  } else if (next.mode === "pathway") {
    const pathway = pathwaysById.get(next.pathway);
    if (!pathway) {
      return null;
    }
    next.lens = null;
    if (next.step && !pathway.steps.some((step) => step.id === next.step)) {
      return null;
    }
    if (!next.step) {
      next.step = pathway.steps[0].id;
      if (next.annotation === pathway.overview_annotation) {
        next.annotation = null;
      }
      next.specificNote = false;
    }
  } else if (next.mode === "all") {
    next.lens = null;
    next.pathway = null;
    next.step = null;
  } else {
    return null;
  }

  const available = annotationKeysForState(next);
  if (!available.length) {
    next.annotation = null;
  } else if (!next.annotation) {
    next.annotation = available[0];
  } else if (!available.includes(next.annotation)) {
    return null;
  }
  return next;
}

function defaultState() {
  return normalizedState(corpusData.presentation.default_state) || {
    text: corpusData.presentation.default_text,
    mode: "plain",
    lens: null,
    pathway: null,
    step: null,
    annotation: null,
    specificNote: false,
  };
}

function stateFromHash() {
  if (!window.location.hash) {
    return null;
  }
  const params = new URLSearchParams(window.location.hash.slice(1));
  return normalizedState({
    text: params.get("text") || corpusData.presentation.default_text,
    mode: params.get("mode"),
    lens: params.get("lens"),
    pathway: params.get("pathway"),
    step: params.get("step"),
    annotation: params.get("note"),
    specificNote: params.has("note"),
  });
}

function stateHash(candidate) {
  const params = new URLSearchParams();
  if (hasMultipleTexts) {
    params.set("text", candidate.text);
  }
  params.set("mode", candidate.mode);
  if (candidate.lens) {
    params.set("lens", candidate.lens);
  }
  if (candidate.pathway) {
    params.set("pathway", candidate.pathway);
  }
  if (candidate.step) {
    params.set("step", candidate.step);
  }
  if (candidate.annotation && (candidate.mode !== "pathway" || candidate.specificNote)) {
    params.set("note", candidate.annotation);
  }
  return `#${params.toString()}`;
}

let state = stateFromHash() || defaultState();

function commitState(candidate, historyMode = "push", shouldScroll = false) {
  const next = normalizedState(candidate) || defaultState();
  state = next;
  const hash = stateHash(state);
  if (historyMode === "replace") {
    history.replaceState(null, "", hash);
  } else if (historyMode === "push") {
    history.pushState(null, "", hash);
  }
  renderReadingState();
  if (shouldScroll && !elements.readingPanel.hidden && window.matchMedia("(max-width: 50rem)").matches) {
    elements.readingPanel.scrollIntoView({behavior: "smooth", block: "start"});
  }
}

function renderMasthead() {
  document.title = `${corpusData.corpus.title} — Review edition`;
  elements.title.textContent = corpusData.corpus.title;
  const title = corpusData.corpus.title.toLocaleLowerCase();
  const visibleAuthors = corpusData.corpus.authors.filter(
    (author) => !title.includes(author.toLocaleLowerCase()),
  );
  elements.author.textContent = visibleAuthors.join(", ");
  elements.author.hidden = visibleAuthors.length === 0;
  elements.description.textContent = corpusData.corpus.description;
  elements.status.replaceChildren(
    makeElement(
      "p",
      "status-line",
      `${corpusData.corpus.review_states.map(humanize).join(", ")} edition · ${corpusData.corpus.annotation_count - 1} notes · ${corpusData.corpus.source_count} sources`,
    ),
  );
}

function selectMode(item) {
  const next = {
    text: state.text,
    mode: item.kind,
    lens: item.kind === "lens" ? item.id : null,
    pathway: item.kind === "pathway" ? item.id : null,
    step: null,
    annotation: null,
    specificNote: false,
  };
  commitState(next, "push", true);
}

function renderReadingNav() {
  elements.readingNav.replaceChildren();
  for (const item of modeItems()) {
    const button = makeElement("button", `reading-nav__item reading-nav__item--${item.kind}`, item.label);
    button.type = "button";
    const active = item.kind === "lens"
      ? state.mode === "lens" && state.lens === item.id
      : item.kind === "pathway"
        ? state.mode === "pathway" && state.pathway === item.id
        : state.mode === item.kind;
    button.setAttribute("aria-pressed", String(active));
    button.addEventListener("click", () => selectMode(item));
    elements.readingNav.append(button);
  }
}

function activeText() {
  return textsById.get(state.text) || textsById.get(corpusData.presentation.default_text);
}

function selectText(textId) {
  commitState({...state, text: textId}, "push");
}

function renderTextSelector() {
  elements.textSelector.replaceChildren();
  elements.textSelector.hidden = !hasMultipleTexts;
  if (!hasMultipleTexts) {
    return;
  }
  elements.textSelector.append(makeElement("span", "text-view-selector__label", "Reading text"));
  for (const text of textViews) {
    const button = makeElement("button", "text-view-selector__button", text.label);
    button.type = "button";
    button.setAttribute("aria-pressed", String(text.id === state.text));
    button.addEventListener("click", () => selectText(text.id));
    elements.textSelector.append(button);
  }
}

function renderWitnessPresentation(text) {
  const presentation = text.witness_presentation;
  elements.witnessPresentation.hidden = !presentation;
  elements.witnessCredit.replaceChildren();
  elements.witnessHeading.replaceChildren();
  if (!presentation) {
    return;
  }

  const credit = [presentation.author, presentation.issued].filter(Boolean).join(" · ");
  elements.witnessCredit.textContent = credit;
  elements.witnessCredit.hidden = !credit;
  elements.witnessHeading.textContent = presentation.heading || "";
  elements.witnessHeading.hidden = !presentation.heading;
}

function renderPoem() {
  const text = activeText();
  const presentation = text.witness_presentation;
  const indentedPositions = new Set(presentation?.stanza_line_indents || []);
  const firstLineNumber = text.lines[0]?.number;
  elements.poem.classList.toggle("poem-lines--historical-forms", text.historical_forms === true);
  renderWitnessPresentation(text);
  elements.poem.replaceChildren();
  for (const line of text.lines) {
    const classes = ["poem-line"];
    if (line.stanza_start) {
      classes.push("poem-line--stanza");
    }
    if (indentedPositions.has(line.stanza_line)) {
      classes.push("poem-line--witness-indent");
    }
    if (presentation?.enlarged_initial && line.number === firstLineNumber) {
      classes.push("poem-line--enlarged-initial");
    }
    const row = makeElement("div", classes.join(" "));
    row.dataset.line = String(line.number);
    row.append(
      makeElement("span", "poem-line__number", String(line.number)),
      makeElement("span", "poem-line__text", line.text),
    );
    elements.poem.append(row);
  }
  updateHighlights();
}

function selectedAnnotation() {
  return state.annotation ? annotationsByKey.get(state.annotation) || null : null;
}

function renderRichText(text, container) {
  const lines = text.split("\n");
  let list = null;
  let paragraphLines = [];

  const flushParagraph = () => {
    if (paragraphLines.length) {
      container.append(makeElement("p", null, paragraphLines.join(" ")));
      paragraphLines = [];
    }
  };

  for (const line of lines) {
    const numbered = line.match(/^\s*\d+\.\s+(.+)$/);
    if (numbered) {
      flushParagraph();
      if (!list) {
        list = document.createElement("ol");
        container.append(list);
      }
      list.append(makeElement("li", null, numbered[1]));
      continue;
    }
    if (!line.trim()) {
      flushParagraph();
      list = null;
      continue;
    }
    list = null;
    paragraphLines.push(line.trim());
  }
  flushParagraph();
}

function renderAttributions(annotation, container) {
  const claim = annotation.claim;
  if (claim.contestation_note) {
    const block = makeElement("div", "contestation");
    block.append(makeElement("p", "eyebrow", "Contested reading"), makeElement("p", null, claim.contestation_note));
    container.append(block);
  }
  if (claim.attributions?.length) {
    const list = makeElement("div", "attribution-list");
    list.append(makeElement("p", "eyebrow", "Positions"));
    for (const attribution of claim.attributions) {
      const paragraph = document.createElement("p");
      paragraph.append(
        makeElement("strong", null, `${attribution.scholar}: `),
        document.createTextNode(attribution.position),
      );
      list.append(paragraph);
    }
    container.append(list);
  }
}

function renderEvidence(evidence, container) {
  const details = makeElement("details", "evidence");
  const sourceLabel = evidence.source.title;
  details.append(makeElement("summary", null, `${sourceLabel} — ${humanize(evidence.relationship)}`));
  const body = makeElement("div", "evidence__body");
  body.append(
    makeElement("p", null, evidence.summary),
    metadataLine("Evidence use", humanize(evidence.use)),
    metadataLine("Access", humanize(evidence.source.access.state)),
    metadataLine("Locator", evidence.citation.locator),
    makeElement("p", "citation", evidence.citation.citation_text),
  );
  if (evidence.source.access.scope_note) {
    body.append(metadataLine("Consulted scope", evidence.source.access.scope_note));
  }
  details.append(body);
  container.append(details);
}

function renderAnnotationApparatus(annotation, container) {
  const apparatus = makeElement("div", "annotation-apparatus");
  apparatus.append(
    makeElement("p", "annotation-kicker", `${humanize(annotation.annotation_type)} · ${humanize(annotation.target.locator.scheme)} ${annotation.target.locator.value}`),
  );
  const meta = makeElement("div", "annotation-meta");
  appendBadge(meta, annotation.claim.epistemic_status, annotation.claim.epistemic_status);
  appendBadge(meta, annotation.review.state);
  if (annotation.claim.contested) {
    appendBadge(meta, "contested");
  }
  apparatus.append(meta);
  container.append(apparatus);
  renderAttributions(annotation, container);

  const confidence = makeElement("div", "editorial-note");
  confidence.append(
    makeElement("p", "eyebrow", `Editorial confidence: ${humanize(annotation.claim.editorial_confidence.level)}`),
    makeElement("p", null, annotation.claim.editorial_confidence.rationale),
  );
  container.append(confidence, makeElement("h4", "evidence-heading", "Evidence trail"));
  for (const evidence of annotation.evidence) {
    renderEvidence(evidence, container);
  }
}

function renderAnnotationContent(annotation, container, collapseApparatus = false, showTitle = true) {
  if (showTitle) {
    container.append(makeElement("h3", null, annotation.title));
  }

  const claimBody = makeElement("div", "claim-body");
  renderRichText(annotation.claim.body, claimBody);
  container.append(claimBody);

  if (!collapseApparatus) {
    renderAnnotationApparatus(annotation, container);
    return;
  }

  const details = makeElement("details", "reading-note__apparatus");
  details.append(makeElement("summary", null, "Sources and editorial notes"));
  const body = makeElement("div", "reading-note__apparatus-body");
  renderAnnotationApparatus(annotation, body);
  details.append(body);
  container.append(details);
}

function highlightedAnnotations() {
  if (state.mode === "pathway") {
    const keys = annotationKeysForState(state);
    if (state.specificNote && state.annotation) {
      const annotation = annotationsByKey.get(state.annotation);
      return annotation ? [annotation] : [];
    }
    return keys.map((key) => annotationsByKey.get(key)).filter(Boolean);
  }
  const annotation = selectedAnnotation();
  return annotation ? [annotation] : [];
}

function updateHighlights() {
  const fragmentsByLine = new Map();
  const linesByNumber = new Map(activeText().lines.map((line) => [line.number, line]));
  for (const annotation of highlightedAnnotations()) {
    const fragments = annotation.target.fragments_by_text?.[state.text] || annotation.target.fragments;
    for (const fragment of fragments) {
      const fragments = fragmentsByLine.get(fragment.line) || [];
      fragments.push({start: fragment.start, end: fragment.end});
      fragmentsByLine.set(fragment.line, fragments);
    }
  }

  for (const row of elements.poem.querySelectorAll(".poem-line")) {
    const line = linesByNumber.get(Number(row.dataset.line));
    const text = row.querySelector(".poem-line__text");
    const fragments = fragmentsByLine.get(line.number) || [];
    if (!fragments.length) {
      text.replaceChildren(document.createTextNode(line.text));
      row.classList.remove("poem-line--active");
      continue;
    }

    fragments.sort((left, right) => left.start - right.start || left.end - right.end);
    const merged = [];
    for (const fragment of fragments) {
      const previous = merged[merged.length - 1];
      if (previous && fragment.start <= previous.end) {
        previous.end = Math.max(previous.end, fragment.end);
      } else {
        merged.push({...fragment});
      }
    }

    const content = [];
    let cursor = 0;
    for (const fragment of merged) {
      content.push(document.createTextNode(line.text.slice(cursor, fragment.start)));
      content.push(makeElement("mark", "poem-target", line.text.slice(fragment.start, fragment.end)));
      cursor = fragment.end;
    }
    content.push(document.createTextNode(line.text.slice(cursor)));
    text.replaceChildren(...content);
    row.classList.add("poem-line--active");
  }
}

function contributorText(source) {
  return source.contributors.map((item) => `${item.name} (${item.role})`).join(", ");
}

function renderSourceRecord(source, container) {
  const details = makeElement("details", "source-record");
  details.append(makeElement("summary", null, source.title));
  const body = makeElement("div", "source-record__body");
  if (source.contributors.length) {
    body.append(metadataLine("Contributors", contributorText(source)));
  }
  body.append(
    metadataLine("Access", humanize(source.access.state)),
    metadataLine("Authority", humanize(source.quality.authority)),
    metadataLine("Review", humanize(source.quality.peer_review_status)),
    metadataLine("Rights", `${humanize(source.rights.status)}; quotation ${humanize(source.rights.quotation)}`),
    makeElement("p", null, source.quality.rationale),
    makeElement("p", "citation", source.citation),
  );
  if (source.access.scope_note) {
    body.append(metadataLine("Consulted scope", source.access.scope_note));
  }
  if (source.notes) {
    body.append(metadataLine("Editorial note", source.notes));
  }
  if (source.canonical_url) {
    const link = makeElement("a", "source-link", "Open source record");
    link.href = source.canonical_url;
    link.target = "_blank";
    link.rel = "noreferrer";
    body.append(link);
  }
  details.append(body);
  container.append(details);
}

function renderSources() {
  elements.sourceList.replaceChildren();
  const accessOrder = ["fully-consulted", "excerpt-consulted", "citation-only", "unavailable"];
  for (const stateName of accessOrder) {
    const group = corpusData.sources.filter((source) => source.access.state === stateName);
    if (!group.length) {
      continue;
    }
    elements.sourceList.append(makeElement("h4", "source-group-heading", `${humanize(stateName)} · ${group.length}`));
    for (const source of group) {
      renderSourceRecord(source, elements.sourceList);
    }
  }
}

function closeSiblingReadingSections(details) {
  for (const sibling of details.parentElement.children) {
    if (sibling !== details && sibling.classList.contains("reading-section")) {
      sibling.open = false;
    }
  }
}

function updatePathwayPrimaryState() {
  for (const details of elements.pathwayDetail.querySelectorAll(".reading-section")) {
    const isPrimary = details.dataset.stepId === state.step;
    details.classList.toggle("reading-section--primary", isPrimary);
    details.querySelector(":scope > summary")?.setAttribute("aria-current", String(isPrimary));
  }
}

function selectPrimaryPathwayStep(details, step) {
  if (details.open) {
    closeSiblingReadingSections(details);
    state = {
      ...state,
      step: step.id,
      annotation: step.annotation_keys[0],
      specificNote: false,
    };
  } else if (state.step === step.id) {
    state = {...state, step: null, annotation: null, specificNote: false};
  }
  history.replaceState(null, "", stateHash(state));
  updatePathwayPrimaryState();
  updateHighlights();
}

function updateAnnotationPrimaryState() {
  for (const details of elements.annotationCollection.querySelectorAll(".reading-section")) {
    const isPrimary = details.dataset.annotationKey === state.annotation;
    details.classList.toggle("reading-section--primary", isPrimary);
    details.querySelector(":scope > summary")?.setAttribute("aria-current", String(isPrimary));
  }
}

function selectAnnotationSection(details, localKey) {
  if (details.open) {
    closeSiblingReadingSections(details);
    state = {...state, annotation: localKey};
  } else if (state.annotation === localKey) {
    state = {...state, annotation: null};
  }
  history.replaceState(null, "", stateHash(state));
  updateAnnotationPrimaryState();
  updateHighlights();
}

function appendReadingSectionSummary(details, index, label) {
  const summary = document.createElement("summary");
  summary.append(
    makeElement("span", "reading-section__number", String(index + 1)),
    makeElement("span", "reading-section__label", label),
  );
  details.append(summary);
  return summary;
}

function renderPathwayDetail() {
  elements.pathwayDetail.replaceChildren();
  const pathway = pathwaysById.get(state.pathway);
  if (!pathway) {
    return;
  }

  const overview = annotationsByKey.get(pathway.overview_annotation);
  if (overview) {
    const introduction = makeElement("div", "pathway-introduction");
    renderRichText(overview.claim.body, introduction);
    elements.pathwayDetail.append(introduction);
  }

  const steps = makeElement("div", "reading-sections pathway-steps");
  pathway.steps.forEach((step, index) => {
    const details = makeElement("details", "reading-section pathway-step");
    details.setAttribute("name", `pathway-${pathway.id}`);
    details.dataset.stepId = step.id;
    details.open = step.id === state.step;
    const summary = appendReadingSectionSummary(details, index, step.label);

    const body = makeElement("div", "reading-section__body");
    for (const localKey of step.annotation_keys) {
      const annotation = annotationsByKey.get(localKey);
      if (!annotation) {
        continue;
      }
      const note = makeElement("article", "reading-note");
      renderAnnotationContent(annotation, note, true);
      body.append(note);
    }
    details.append(body);
    summary.addEventListener("click", () => {
      window.requestAnimationFrame(() => selectPrimaryPathwayStep(details, step));
    });
    steps.append(details);
  });
  elements.pathwayDetail.append(steps);
  updatePathwayPrimaryState();
}

function renderAnnotationCollection() {
  elements.annotationCollection.replaceChildren();
  const keys = annotationKeysForState(state);
  if (!keys.length) {
    elements.annotationCollection.append(makeElement("p", "annotation-collection__empty", "No annotations in this view."));
    return;
  }

  for (const [index, localKey] of keys.entries()) {
    const annotation = annotationsByKey.get(localKey);
    if (!annotation) {
      continue;
    }
    const details = makeElement("details", "reading-section annotation-section");
    details.setAttribute("name", `annotations-${state.mode}-${state.lens || "all"}`);
    details.dataset.annotationKey = localKey;
    details.open = localKey === state.annotation;
    const summary = appendReadingSectionSummary(details, index, annotation.title);
    const body = makeElement("div", "reading-section__body");
    const note = makeElement("article", "reading-note");
    renderAnnotationContent(annotation, note, true, false);
    body.append(note);
    details.append(body);
    summary.addEventListener("click", () => {
      window.requestAnimationFrame(() => selectAnnotationSection(details, localKey));
    });
    elements.annotationCollection.append(details);
  }
  updateAnnotationPrimaryState();
}

function renderReadingState() {
  const item = activeModeItem();
  renderTextSelector();
  renderPoem();
  elements.witness.textContent = activeText().provenance_note;
  const showModeDescription = state.mode === "lens" && Boolean(item?.description);
  elements.modeDescription.textContent = showModeDescription ? item.description : "";
  elements.modeDescription.hidden = !showModeDescription;

  const showingPlain = state.mode === "plain";
  const showingPathway = state.mode === "pathway";
  const showingSources = state.mode === "sources";
  const showingAnnotations = state.mode === "lens" || state.mode === "all";
  elements.shell.classList.toggle("edition-shell--plain", showingPlain);
  elements.readingPanel.hidden = showingPlain;
  elements.pathwayDetail.hidden = !showingPathway;
  elements.readingGrid.hidden = showingPathway;
  elements.sourceDetail.hidden = !showingSources;
  elements.annotationCollection.hidden = !showingAnnotations;

  renderReadingNav();
  if (showingPathway) {
    renderPathwayDetail();
  } else if (showingSources) {
    renderSources();
  } else if (showingAnnotations) {
    renderAnnotationCollection();
  }
  updateHighlights();
}

function restoreLocationState() {
  state = stateFromHash() || defaultState();
  history.replaceState(null, "", stateHash(state));
  renderReadingState();
}

renderMasthead();
commitState(state, "replace");
window.addEventListener("popstate", restoreLocationState);
window.addEventListener("hashchange", restoreLocationState);
