import pyparsing as pp

pp.ParserElement.setDefaultWhitespaceChars("\r\n")

RE = pp.Regex

QUOTED_CHAR_BRE = RE(r"\\[.^*\[\]\\$]")
QUOTED_CHAR_ERE = RE(r"\\[.^\\\[\]$()|*+?{}]")

SPEC_CHAR_BRE = r"\.\[^$*"
ORD_CHAR_BRE = RE(r"[^%s]" % SPEC_CHAR_BRE)
SPEC_CHAR_BRE = RE(r"[%s]" % SPEC_CHAR_BRE)

SPEC_CHAR_ERE = r".^\[$()|*+?{\\"
ORD_CHAR_ERE = RE(r"[^%s]" % SPEC_CHAR_ERE)
# SPEC_CHAR_ERE = RE(r'[%s]' % SPEC_CHAR_ERE)

# At least in python... see http://docs.python.org/library/re.html
SPEC_CHAR_PYTHON_ERE = RE(r"\\[AbBdDsSwWZ]")
# SPEC_CHAR_PYTHON_STRING = RE(r'\[abfnrtvx]|\[0-7]{3}\\0[0-7]|\\x[0-9a-fA-F]{2}')
SPEC_CHAR_PYTHON_STRING = RE(r"\\[abfnrtvx]")

BACKREF = RE(r"\\[0-9]")
DUP_COUNT = RE(r"\b[0-9]+\b")
META_CHAR = RE(r"[-^\]]")

COLL_ELEM = RE(r"[^-^\]]")
L_ANCHOR = pp.Literal("^")
R_ANCHOR = pp.Literal("$")

LBRACK = pp.Literal("[")
RBRACK = pp.Literal("]")

ERE_LPAREN = pp.Literal("(")
ERE_RPAREN = pp.Literal(")")
ERE_LBRACE = pp.Literal("{")
ERE_RBRACE = pp.Literal("}")

ALTERATION = pp.Literal("|")

CFLEX = pp.Literal("^")
HYPHEN = pp.Literal("-")
KLEENE_STAR = pp.Literal("*")
PLUS = pp.Literal("+")
QMARK = pp.Literal("?")
COMMA = pp.Literal(",")
DOT = pp.Literal(".")

posix_special_classes = [
    "alnum",
    "alpha",
    "blank",
    "cntrl",
    "digit",
    "graph",
    "lower",
    "print",
    "punct",
    "space",
    "upper",
    "xdigit",
]

class_name = pp.oneOf(" ".join(posix_special_classes))

Open_dot = pp.Literal("[.")
Dot_close = pp.Literal(".]")
collating_symbol = Open_dot + COLL_ELEM + Dot_close


Open_equal = pp.Literal("[=")
Equal_close = pp.Literal("=]")
equivalence_class = Open_equal + COLL_ELEM + Equal_close


Open_colon = pp.Literal("[:")
Colon_close = pp.Literal(":]")
character_class = Open_colon + class_name + Colon_close


class BaseREParser(object):
    parser = None

    def __init__(self, handler_object):
        self.handler_object = handler_object
        self.py_string_escape = SPEC_CHAR_PYTHON_STRING.copy().setParseAction(
            self.handler_object.handleStringEscape
        )
        end_range = COLL_ELEM ^ collating_symbol ^ self.py_string_escape  # added by me
        start_range = end_range + HYPHEN
        range_expression = start_range + end_range ^ start_range + HYPHEN
        single_expression = (
            end_range ^ character_class ^ equivalence_class ^ self.py_string_escape
        )  # added by me
        expression_term = single_expression ^ range_expression.setParseAction(
            self.handler_object.handleRange
        )

        # Pyparsing doesn't like "left recursion"
        # follow_list = pp.Forward()
        # follow_list << ( expression_term | follow_list + expression_term )

        # but this is clearer, anyway
        follow_list = pp.OneOrMore(expression_term)
        bracket_list = follow_list + pp.Optional(HYPHEN)
        matching_list = bracket_list
        nonmatching_list = CFLEX + bracket_list
        bracket_expression = LBRACK + (matching_list ^ nonmatching_list) + RBRACK
        self.bracket_expression = pp.Group(
            bracket_expression.setParseAction(self.handler_object.handleBracketList)
        )

    def parse(self, s):
        self.handler_object.startParsing(s)
        self.parser.parseString(s)
        self.handler_object.endParsing()


class ExtendedREParser(BaseREParser):
    def __init__(self, handler_object):
        BaseREParser.__init__(self, handler_object)
        # self.escape_ere = SPEC_CHAR_ERE.copy().setParseAction(self.handler_object.handleReEscape)
        self.py_ere = SPEC_CHAR_PYTHON_ERE.copy().setParseAction(
            self.handler_object.handleReEscape
        )
        self.backref = BACKREF.copy().setParseAction(
            self.handler_object.handleBackreference
        )
        ERE_dupl_symbol = pp.Or(
            [
                KLEENE_STAR,
                PLUS,
                QMARK,
                ERE_LBRACE + DUP_COUNT + ERE_RBRACE,
                ERE_LBRACE + DUP_COUNT + COMMA + ERE_RBRACE,
                ERE_LBRACE + DUP_COUNT + COMMA + DUP_COUNT + ERE_RBRACE,
            ]
        ).setParseAction(self.handler_object.handleDupl)

        one_character_ERE = pp.Or(
            [
                ORD_CHAR_ERE,
                QUOTED_CHAR_ERE,
                DOT,
                self.py_ere,
                self.py_string_escape,
                self.backref,  # these weren't in my reference grammar...
                self.bracket_expression,
            ]
        )

        extended_reg_exp = pp.Forward()

        # Pyparsing pukes on this one... had to do it differently
        # It's that left recursion again...
        # ERE_expression = pp.Forward()
        # ERE_expression << pp.Or([ one_character_ERE , L_ANCHOR , R_ANCHOR ,
        #            ERE_LPAREN + extended_reg_exp + ERE_RPAREN ,
        #            ERE_expression + ERE_dupl_symbol ])

        # Straying slightly from the reference grammar here, since I don't see any
        # reason to allow for *_ANCHOR + ERE_dupl_symbol, which is nonsensical IMHO
        ERE_expression = pp.Or(
            [
                one_character_ERE + pp.Optional(ERE_dupl_symbol),
                L_ANCHOR,
                R_ANCHOR,
                pp.Group(
                    (ERE_LPAREN + extended_reg_exp + ERE_RPAREN).setParseAction(
                        self.handler_object.handleGroup
                    )
                )
                + pp.Optional(ERE_dupl_symbol),
            ]
        )

        # bad_lparen = ERE_LPAREN.copy().setParseAction(self.handler_object.handleInvalid)
        # bad_rparen = ERE_RPAREN.copy().setParseAction(self.handler_object.handleInvalid)

        # Yet again...
        # ERE_branch = pp.Forward()
        # ERE_branch << ( ERE_expression ^ ERE_branch + ERE_expression )
        ERE_branch = pp.OneOrMore(ERE_expression)

        # extended_reg_exp << pp.Or([ ERE_branch , extended_reg_exp + ALTERATION + ERE_branch ])
        extended_reg_exp << (
            ERE_branch + pp.Optional(pp.OneOrMore(ALTERATION + ERE_branch))
        )

        # extended_reg_exp_invalid = pp.OneOrMore( (bad_lparen + extended_reg_exp) ^ (extended_reg_exp + bad_rparen) )
        invalid = RE(".+").setParseAction(self.handler_object.handleInvalid)

        self.parser = (
            pp.LineStart() + extended_reg_exp + pp.Optional(invalid) + pp.LineEnd()
        )


def toklen(toks):
    if type(toks) in (bytes, str):
        return len(toks)
    tlen = 0
    for t in toks:
        # print type(toks), type(t)
        tlen += toklen(t)
    return tlen


class TestHandlerObject(object):
    # NOTE: exceptions seem to be caught and ignored by pyparsing...
    def startParsing(self, s):
        self.formatting = []
        self.string = s
        self.groups = {}

    def endParsing(self):
        print((" " * 9).join(map(str, list(range(8)))))
        print("".join(["0123456789" for i in range(8)]))

        print(self.string)
        print(self.formatting)

        print(self.groups)

    def handleType(self, s, loc, toks, t_name):
        # s   = the original string being parsed (see note below)
        # loc = the location of the matching substring
        # toks = a list of the matched tokens, packaged as a ParseResults object
        print(s)
        print(loc)
        print(toks)
        self.formatting.insert(
            0,
            (
                t_name,
                loc,
                toklen(toks[0]),
                loc + toklen(toks) - toklen(toks[-1]),
                toklen(toks[-1]),
            ),
        )

    def handleDupl(self, s, loc, toks):
        self.handleType(s, loc, toks, "dupl")

    def handleGroup(self, s, loc, toks):
        self.groups[loc] = toklen(toks)
        self.handleType(s, loc, toks, "group")

    def handleBracketList(self, s, loc, toks):
        self.handleType(s, loc, toks, "bracket")


class ReplacePatternParser(BaseREParser):
    def __init__(self, handler):
        BaseREParser.__init__(self, handler)
        backref = BACKREF.copy().setParseAction(self.handler_object.handleBackreference)
        self.py_string_escape.setParseAction(self.handler_object.handleStringEscape)
        valid_char = RE(r"[^\\]")
        invalid_escape = RE(r"\\.").setParseAction(self.handler_object.handleInvalid)
        self.parser = pp.OneOrMore(
            backref | self.py_string_escape | invalid_escape | valid_char
        )  # | is like or (^), but takes the first possible match
