"""Replace this adapter once the course API details are confirmed.

Future implementation must use only retrieved evidence, treat user/source text
as untrusted, and return validated passage IDs rather than invented citations.
Never send credentials to the browser or log them.
"""


class ModelNotConfigured(Exception):
    pass


def generate_answer(question, passages):
    raise ModelNotConfigured("The model API has not been connected yet.")
