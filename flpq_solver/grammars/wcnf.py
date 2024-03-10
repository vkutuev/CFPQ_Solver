"""Module contains base class for grammar in Weak Chomsky Normal Form"""

from pyformlang.cfg import CFG, Variable, Terminal, Epsilon, Production

__all__ = [
    "WCNF",
]


class WCNF:
    """
    A Context-Free Grammar class in which products take the following form:
    - *A -> B C*
    - *A -> a*
    - *A -> epsilon*
    where `A`, `B` and `C` are variables; `a` is an arbitrary terminal

    Also known as Weak Chomsky Normal Form
    """

    start_variable: Variable
    """Grammar start nonterminal"""

    epsilon_productions: list[Production]
    """List of productions have form

    *A -> epsilon*
    """

    unary_productions: list[Production]
    """List of productions have form

    *A -> a*
    """

    binary_productions: list[Production]
    """List of productions have form

    *A -> B C*
    """

    variables: list[Variable]
    """List of all nonterminals
    """

    terminals: list[Terminal]
    """List of all terminals
    """

    def __init__(self, cfg: CFG):
        """
        Create a grammars in WCNF from  that generates an equivalent language

        :param cfg: Context-Free Grammar
        """
        self._cfg: CFG = cfg
        self.start_variable = cfg.start_symbol

        cnf = cfg if _is_in_wcnf(cfg) else cfg.to_normal_form()

        self.epsilon_productions = []
        self.unary_productions = []
        self.binary_productions = []

        for production in self._cfg.productions:
            if (
                production.body in ([], Epsilon)
                and production not in self.epsilon_productions
            ):
                self.epsilon_productions.append(production)

        for production in cnf.productions:
            if len(production.body) == 1 and production not in self.unary_productions:
                self.unary_productions.append(production)
            elif (
                len(production.body) == 2 and production not in self.binary_productions
            ):
                self.binary_productions.append(production)

        productions = (
            self.epsilon_productions + self.unary_productions + self.binary_productions
        )

        self.variables = []
        self.terminals = []

        for production in productions:
            if production.head not in self.variables:
                self.variables.append(production.head)

            for term in production.body:
                if isinstance(term, Terminal) and term not in self.terminals:
                    self.terminals.append(term)
                elif isinstance(term, Variable) and term not in self.variables:
                    self.variables.append(term)

        self.variables.sort(key=str)
        self.terminals.sort(key=str)
        self.epsilon_productions.sort(key=str)
        self.unary_productions.sort(key=str)
        self.binary_productions.sort(key=str)

    def contains(self, word: str) -> bool:
        """
        Checks if `word` is derived in this grammar.

        :param word: The word to check
        :return: Whether word if in the CFG or not
        """
        return self._cfg.contains(map(Terminal, word))

    @classmethod
    def from_text(cls, text: str, start_variable: Variable = Variable("S")) -> "WCNF":
        """Build a WCNF object from a CFG represented in string.
        The `text` contains one production per line.

        The structure of a production is:

        `head -> body`

        :param text: The CFG represented in string
        :param start_variable: The start nonterminal in the grammar
        :return: A WCNF object
        """
        cfg = CFG.from_text(text, start_variable)
        return cls(cfg)


def _is_in_wcnf(cfg: CFG) -> bool:
    """
    Checks if the `cfg` is in WCNF.

    :param cfg: The context free grammar to check
    :return: Whether `cfg` is in WCNF
    """
    for production in cfg.productions:
        if len(production.body) > 2:
            return False
        if len(production.body) == 2:
            if not (
                isinstance(production.body[0], Variable)
                and isinstance(production.body[1], Variable)
            ):
                return False
        if len(production.body) == 1:
            if not isinstance(production.body[0], Terminal):
                return False
    return True
