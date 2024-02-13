from Parsers.SubsPleaseParser import SUBS_PLEASE_PARSER_NAME, SubsPleaseParser
from ParserBase import ParserBase

PARSER_MAP: dict[str, ParserBase] = {
    SUBS_PLEASE_PARSER_NAME: SubsPleaseParser
}

def get_parser_by_name(parser_name) -> ParserBase:
    return PARSER_MAP[parser_name]()