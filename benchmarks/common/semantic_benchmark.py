from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Optional, Union

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS


# ---------------------------------------------------------------------------
# Namespace declarations
# ---------------------------------------------------------------------------

M4I     = Namespace("http://w3id.org/nfdi4ing/metadata4ing#")
MATHMOD = Namespace("https://mardi4nfdi.de/mathmoddb#")
OBO     = Namespace("http://purl.obolibrary.org/obo/")

HAS_NUMERICAL_VALUE = M4I.hasNumericalValue
HAS_STRING_VALUE    = M4I.hasStringValue
HAS_UNIT            = M4I.hasUnit
HAS_KIND_OF_QTY     = M4I.hasKindOfQuantity
HAS_PART            = OBO.BFO_0000051
USES_CONFIG         = M4I.usesConfiguration
HAS_EMPLOYED_TOOL   = M4I.hasEmployedTool
INVESTIGATES        = M4I.investigates
EVALUATES           = M4I.evaluates
USES                = URIRef("https://mardi4nfdi.de/mathmoddb#uses")
DESCRIBED_BY        = URIRef("https://mardi4nfdi.de/mathmoddb#describedAsDocumentedBy")

T_BENCHMARK          = M4I.Benchmark
T_PARAMETER_SET      = M4I.ParameterSet
T_NUMERICAL_VARIABLE = M4I.NumericalVariable
T_PROCESSING_STEP    = M4I.ProcessingStep


# ---------------------------------------------------------------------------
# Domain Classes
# ---------------------------------------------------------------------------

@dataclass
class KGNode:
    id: str
    label: Optional[str] = None


@dataclass
class ResearchProblem(KGNode):
    pass


@dataclass
class MathematicalModel(KGNode):
    pass


@dataclass
class Publication(KGNode):
    pass


@dataclass
class NumericalVariable(KGNode):
    unit: Optional[str] = None
    quantity_kind: Optional[str] = None


@dataclass
class NumericalParameter(KGNode):
    numerical_value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class TextParameter(KGNode):
    string_value: Optional[str] = None


ParameterEntry = Union[NumericalParameter, TextParameter, NumericalVariable]


@dataclass
class ParameterSet(KGNode):
    label: Optional[str] = None
    parts: list[ParameterEntry] = field(default_factory=list)


@dataclass
class Tool(KGNode):
    pass


@dataclass
class ProcessingStep(KGNode):
    configurations: list[ParameterSet] = field(default_factory=list)
    employed_tools: list[Tool] = field(default_factory=list)


@dataclass
class BenchmarkSemantic(KGNode):
    investigates: Optional[ResearchProblem] = None
    uses: Optional[MathematicalModel] = None
    evaluates: list[NumericalVariable] = field(default_factory=list)
    parameter_sets: list[ParameterSet] = field(default_factory=list)
    described_by: Optional[Publication] = None
    processing_steps: list[ProcessingStep] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Loader Class (NEW)
# ---------------------------------------------------------------------------

class BenchmarkLoader:
    def __init__(self, jsonld_path: str | pathlib.Path):
        self.path = pathlib.Path(jsonld_path)

        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")

        self.graph = Graph()
        self.graph.parse(str(self.path), format="json-ld")
        
        for s,p,o in self.graph:
            print(s, p, o)

    def _str(self, uri: URIRef) -> str:
        return str(uri)

    def _label(self, subject: URIRef) -> Optional[str]:
        # print(f"Getting label for {subject}")
        val = self.graph.value(subject, RDFS.label)
        return str(val) if val else None

    def _scalar(self, subject: URIRef, predicate: URIRef):
        val = self.graph.value(subject, predicate)
        if val is None:
            return None
        return val.toPython() if isinstance(val, Literal) else str(val)

    def build_numerical_parameter(self, uri: URIRef) -> NumericalParameter:
        return NumericalParameter(
            id=self._str(uri),
            label=self._label(uri),
            numerical_value=self._scalar(uri, HAS_NUMERICAL_VALUE),
            unit=self._scalar(uri, HAS_UNIT),
        )

    def build_text_parameter(self, uri: URIRef) -> TextParameter:
        return TextParameter(
            id=self._str(uri),
            label=self._label(uri),
            string_value=self._scalar(uri, HAS_STRING_VALUE),
        )

    def build_numerical_variable(self, uri: URIRef) -> NumericalVariable:
        return NumericalVariable(
            id=self._str(uri),
            label=self._label(uri),
            unit=self._scalar(uri, HAS_UNIT),
            quantity_kind=self._scalar(uri, HAS_KIND_OF_QTY),
        )

    def build_parameter_entry(self, uri: URIRef) -> ParameterEntry:
        if self.graph.value(uri, HAS_STRING_VALUE):
            return self.build_text_parameter(uri)
        if (uri, RDF.type, T_NUMERICAL_VARIABLE) in self.graph:
            return self.build_numerical_variable(uri)
        return self.build_numerical_parameter(uri)

    def build_parameter_set(self, uri: URIRef) -> ParameterSet:
        label = self._label(uri)
        parts = [
            self.build_parameter_entry(part)
            for part in self.graph.objects(uri, HAS_PART)
        ]
        return ParameterSet(id=self._str(uri), label=label, parts=parts)

    def build_tool(self, uri: URIRef) -> Tool:
        return Tool(id=self._str(uri), label=self._label(uri))

    def build_processing_step(self, uri: URIRef) -> ProcessingStep:
        configs = [
            self.build_parameter_set(c)
            for c in self.graph.objects(uri, USES_CONFIG)
        ]
        tools = [
            self.build_tool(t)
            for t in self.graph.objects(uri, HAS_EMPLOYED_TOOL)
        ]
        return ProcessingStep(
            id=self._str(uri),
            label=self._label(uri),
            configurations=configs,
            employed_tools=tools,
        )

    def load(self) -> BenchmarkSemantic:
        g = self.graph

        bm_uri = next(g.subjects(RDF.type, T_BENCHMARK), None)
        if bm_uri is None:
            raise ValueError("No m4i:Benchmark node found.")

        rp_uri = g.value(bm_uri, INVESTIGATES)
        mm_uri = g.value(bm_uri, USES)
        pub_uri = g.value(bm_uri, DESCRIBED_BY)

        research_problem = (
            ResearchProblem(id=self._str(rp_uri), label=self._label(rp_uri))
            if rp_uri else None
        )

        math_model = (
            MathematicalModel(id=self._str(mm_uri), label=self._label(mm_uri))
            if mm_uri else None
        )

        publication = (
            Publication(id=self._str(pub_uri), label=self._label(pub_uri))
            if pub_uri else None
        )

        metrics = [
            self.build_numerical_variable(m)
            for m in g.objects(bm_uri, EVALUATES)
        ]

        param_sets = [
            self.build_parameter_set(ps)
            for ps in g.objects(bm_uri, M4I.hasParameterSet)
        ]

        steps = [
            self.build_processing_step(s)
            for s in g.subjects(RDF.type, T_PROCESSING_STEP)
        ]

        return BenchmarkSemantic(
            id=self._str(bm_uri),
            label=self._label(bm_uri),
            investigates=research_problem,
            uses=math_model,
            evaluates=metrics,
            parameter_sets=param_sets,
            described_by=publication,
            processing_steps=steps,
        )