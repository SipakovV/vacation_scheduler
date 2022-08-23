from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, NamedStyle

thin = Side(border_style="thin", color="000000")
thicc = Side(border_style="thick", color="000000")

remarks_font = Font(name='Arial Cyr',
                    size=6,
                    bold=False,
                    italic=False,
                    vertAlign=None,
                    underline='none',
                    strike=False,
                    color='FF000000')

default_entry_style = NamedStyle(name="default_entry_style")
default_entry_style.font = Font(name='Arial Cyr',
                                size=9,
                                bold=False,
                                italic=False,
                                vertAlign=None,
                                underline='none',
                                strike=False,
                                color='FF000000')

default_entry_style.border = Border(left=thin,
                                    top=thin,
                                    right=thin,
                                    bottom=thin)

default_entry_style.alignment = Alignment(horizontal='left',
                                          vertical='top',
                                          text_rotation=0,
                                          wrap_text=True,
                                          shrink_to_fit=False,
                                          indent=0)
