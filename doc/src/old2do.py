"""
Transform Hjorten's Beamer slides to doconce format.
"""
import re, sys

def transform(filestr):
    # Get rid of ^M
    filestr = re.sub(r'\r', '', filestr)
    # Remove comments
    filestr = re.sub(r'^%.*$', '', filestr, flags=re.MULTILINE)
    # Remove trailing }
    filestr = re.sub(r'^ *\} *$', '', filestr, flags=re.MULTILINE)

    filestr = re.sub(r'^ *(\\\[|\\begin\{equation\*?\}|\\begin\{eqnarray\*?\})',
                     r'\n!bt\n\g<1>', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^ *(\\\]|\\end\{equation\*?\}|\\end\{eqnarray\*?\})',
                     r'\g<1>\n!et', filestr, flags=re.MULTILINE)

    # Remove \item in lists with code or math
    pattern = r'(\\begin\{itemize\}|\\bit)(.+?)(\\end\{itemize\}|\\eit)'
    def subst(m):
        begin, items, end = m.groups()
        if not 'erbatim}' in items and not '!bt' in items:
            return m.group()  # no changes, return the entire match
        else:
            items = re.sub(r'\\item\s+', '\n', items)
            return begin + items + end
    filestr = re.sub(pattern, subst, filestr, flags=re.DOTALL)

    filestr = re.sub(r'^ *\{\\scriptsize', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^ *\\(begin|end)\{(small|center|figure)\}', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^\\lstset\{.+$', '', filestr, flags=re.MULTILINE)
    filestr = filestr.replace('lstlisting', 'verbatim')

    filestr = re.sub(r'^\\frame\s+\{', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^\\frame\[.+?\{', '', filestr, flags=re.MULTILINE|re.DOTALL)
    filestr = re.sub(r'\\url\{([^}]+?)\}', 'URL: "\g<1>"', filestr)
    filestr = re.sub(r'\\noindent\s*', '', filestr)
    filestr = re.sub(r'\.~', '. ', filestr)
    # \bs{title} -> ===== title =====
    filestr = re.sub(r'^ *\\section\{(.+?)\}', '!split\n======= \g<1> =======',
                     filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^ *\\frametitle\{([^}]+)\}', '!split\n===== \g<1> =====\n',
                     filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^ *\\begin\{block\}\{(.*?)\}', '!bblock \g<1>', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^ *\\end\{block\}', '!eblock', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^ *\\includegraphics\[(scale|width)=(.+?)\]\{(.+?)\}',
                     'FIGURE: [\g<3>, width=500 frac=\g<2>]', filestr,
                     flags=re.MULTILINE)
    # Turn eqnarray to align (req. by mathjax)
    filestr = re.sub(r'\\begin\{eqnarray(\*?)\}', r'\\begin{align\g<1>}', filestr)
    filestr = re.sub(r'\\end\{eqnarray(\*?)\}', r'\end{align\g<1>}', filestr)
    filestr = re.sub(r'& *= *&', '&=', filestr)

    # \def -> \newcommand
    filestr = re.sub(r'^\\def(\\.+?)\{(.+)$', r'\\newcommand{\g<1>}{\g<2>',
                     filestr, flags=re.MULTILINE)

    # \begin{slide}{title} -> ===== title =====
    filestr = re.sub(r'\\begin\{slide\}\{(.+?)\}', '===== \g<1> =====', filestr)

    filestr = re.sub(r'\\begin\{(itemize|enumerate)\}', '', filestr)
    filestr = re.sub(r'\\end\{(itemize|enumerate)\}', '', filestr)
    filestr = re.sub(r'\\newline', '', filestr)
    filestr = re.sub(r'\\es\n', '\n', filestr)
    filestr = re.sub(r'\\end\{slide\}\n', '\n\n', filestr)
    # \emph{...}, {\em ...} -> *...*
    filestr = re.sub(r'\\emph\{([^}]+?)\}', '*\g<1>*', filestr)
    filestr = re.sub(r'\{\\em ([^}]+?)\}', '*\g<1>*', filestr)
    # Assume bold is often inline verbatim
    #filestr = re.sub(r'\{\\bf ([^}]+?)\}', '`\g<1>`', filestr)
    filestr = re.sub(r'\\lstinline\{([^}]+?)\}', '`\g<1>`', filestr)
    # \begin{Verbatim} -> !bc LANG (change LANG manually according to language)
    filestr = re.sub(r'\\begin\{[Vv]erbatim.+', '\n!bc cppcod', filestr)
    filestr = re.sub(r'\\end\{[Vv]erbatim.+', '!ec', filestr)
    # \\ -> <linebreak>
    #filestr = re.sub(r'\\\\\n', '<linebreak>\n', filestr)
    #filestr = re.sub(r'\\\\', 'LINEBREAK!', filestr)  # must be changed manually
    filestr = re.sub(r' \\& ', ' & ', filestr)
    filestr = re.sub(r'\\vspace\{(.+?)\}', '', filestr, flags=re.DOTALL)

    # Make all \item lines one line (look ahead)
    # (keep an extra \n before \eit or slide title)
    pattern = r'^ *\\item (.+?)(?=(\\item|\n\\eit|\n\\end\{itemize\}|\n!eblock|\n=====))'
    def subst(m):
        # Make one line and condense multiple spaces to one, i.e.,
        # \s+ -> ' '; must add final \n to avoid everything on one line
        return r'\item ' + re.sub(r'\s+', ' ', m.group(1)) + '\n'
    filestr = re.sub(pattern, subst, filestr, flags=re.DOTALL|re.MULTILINE)
    # \item -> *
    filestr = re.sub(r'\\item', '  *', filestr)
    filestr = re.sub(r'\n\n+', '\n\n', filestr)
    filestr = re.sub(r'(!bblock.*)\n+', '\g<1>\n', filestr)
    filestr = re.sub(r'\n+!eblock', '\n!eblock', filestr)

    return filestr

filename = sys.argv[1]
filestr = open(filename).read()
print transform(filestr)
