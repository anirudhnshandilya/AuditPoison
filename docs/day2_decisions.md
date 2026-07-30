# Day-2 design decisions

## Balanced evaluation slice

Day 1 intentionally contained only non-compliant or insufficient-evidence oracles. Day 2 adds ten compliant clean scenarios and one harmless transformation of each. The resulting 40-bundle pilot is balanced at the security decision boundary: 20 compliant versus 20 cases where compliant assurance is unsafe. The three-class distribution remains 20 compliant, 15 non-compliant, and 5 insufficient-evidence.

## Benign stability pairs

Benign variants preserve all control-relevant facts while changing presentation or adding harmless information. They cover formatting noise, evidence reordering, irrelevant context, duplicated support, semantic paraphrase, and metadata noise. These pairs measure whether a model is brittle even without an attacker.

## No oracle leakage

The model runner exposes only bundle_id, control, scope, and evidence. Oracle labels, predicates, attack metadata, perturbation metadata, and expected secure behaviour never enter the evaluated prompt.

## Provider neutrality

The benchmark does not hard-code a commercial API. A command adapter sends one JSON request on stdin and accepts one JSON response on stdout. This permits wrappers for hosted APIs, local inference servers, or reproducible offline models without changing benchmark logic.

## Reporting gate

The keyword baseline and demo command adapter are pipeline checks only. Neither may be described as a scientific model baseline in the paper.
