#pragma once
namespace gfx::abstraction {
// Marker types only. These define architectural roles; they are not runtime roots.
struct PrimitiveForm {};
struct BindingForm {};
struct RelationForm {};
struct ReferenceForm {};
struct ValidationForm {};
struct ProvenanceForm {};
struct CompositionForm {};
struct DecompositionForm {};
struct ActivationForm {};
struct ContinuationForm {};
struct ProgressForm {};
struct RecursionForm {};

struct GenericModifier {};
struct PolymorphicModifier {};
}
