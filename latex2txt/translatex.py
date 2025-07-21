#!/usr/bin/env python
import latex_process
import text_process
from latex_process import environment_list, command_list, format_list
from encode_process import get_file_encoding
import re
import cache
import tqdm.auto
import concurrent.futures

default_begin = r'''
\documentclass[UTF8]{article}
\usepackage{xeCJK}
\usepackage{amsmath,amssymb}
\begin{document}
'''
default_end = r'''
\end{document}
'''

math_code = 'XMATHX'
mularg_command_list = [('textcolor', 2, (1, ))]



class LatexTranslator:

    def __init__(self, debug=False, threads=0, char_limit=2000):
        self.num = None
        self.theorems = None
        self.debug = debug
        self.char_limit = char_limit
        if self.debug:
            self.f_old = open("text_old", "w", encoding='utf-8')
            self.f_new = open("text_new", "w", encoding='utf-8')
            self.f_obj = open("objs", "w", encoding='utf-8')
        self.threads = threads if threads > 0 else None

        if threads == 0:
            self.threads = None
        else:
            self.threads = threads


    def close(self):
        if self.debug:
            self.f_old.close()
            self.f_new.close()
            self.f_obj.close()

    def translate_paragraph_text(self, text):

        lines = text.split('\n')
        parts = []
        part = ''
        for line in lines:
            if len(line) >= self.char_limit:
                raise ValueError("One line is too long")
            if len(part) + len(line) < self.char_limit - 10:
                part = part + '\n' + line if part else line
            else:
                parts.append(part)
                part = line
        parts.append(part)

        parts_cleaned = [p.strip() for p in parts]
        text_processed = '\n'.join(parts_cleaned)
        return text_processed.replace("\u200b", "")



    def replace_with_uppercase(self, text, word):
        # Construct a regex pattern that matches the word regardless of case
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        # Replace all matches with the uppercase version of the word
        result = pattern.sub(word.upper(), text)
        return result



    def extract_translatable_text(self, latex_original_paragraph):

        for format_name in format_list:
            latex_original_paragraph = latex_process.delete_specific_format(latex_original_paragraph, format_name)

        text_original_paragraph, objs = latex_process.replace_latex_objects(latex_original_paragraph)
        text_original_paragraph = latex_process.combine_split_to_sentences(text_original_paragraph)
        text_original_paragraph = text_process.split_too_long_paragraphs(text_original_paragraph)

        if not self.complete:
            text_original_paragraph = text_process.split_titles(text_original_paragraph)


        text_original_paragraph = re.sub(r'  +', ' ', text_original_paragraph)


        if self.debug:
            print(f'\n\nParagraph {self.num}\n\n', file=self.f_old)
            print(text_original_paragraph, file=self.f_old)

        return text_original_paragraph


    def split_latex_to_paragraphs(self, latex):

        text, _ = latex_process.replace_latex_objects(latex)  # 忽略 objs
        paragraphs_text = re.split(r'\n\n+', text)
        return paragraphs_text


    def translate_text_in_paragraph_latex(self, paragraph):

        splited_paragraphs, seps = latex_process.split_by_command(paragraph)
        result = ''
        for split, sep in zip(splited_paragraphs, seps):
            result += self.extract_translatable_text(split) + ' ' + sep + ' '

        return result

    def translate_text_in_paragraph_latex_and_leading_brace(self, latex_original_paragraph):
        cleaned_text = self.translate_text_in_paragraph_latex(latex_original_paragraph)
        return latex_process.process_leading_level_brace(cleaned_text,
                                                         self.translate_text_in_paragraph_latex_and_leading_brace)

    def translate_latex_all_objects(self, latex):

        translate_function = self.translate_text_in_paragraph_latex_and_leading_brace
        for env_name in environment_list + self.theorems:
            latex = latex_process.process_specific_env(latex, translate_function, env_name)
            latex = latex_process.process_specific_env(latex, translate_function, env_name + r'\*')
        for command_name in command_list:
            latex = latex_process.process_specific_command(latex, translate_function, command_name)
            latex = latex_process.process_specific_command(latex, translate_function, command_name + r'\*')
        for command_group in mularg_command_list:
            latex = latex_process.process_mularg_command(latex, translate_function, command_group)

        return latex


    def translate_paragraph_latex(self, latex_original_paragraph):
        latex_cleaned = self.translate_text_in_paragraph_latex_and_leading_brace(latex_original_paragraph)
        latex_cleaned = self.translate_latex_all_objects(latex_cleaned)
        return latex_cleaned


    def worker(self, latex_original_paragraph):
        try:
            text_only, _ = latex_process.replace_latex_objects(latex_original_paragraph)


            text_only = latex_process.combine_split_to_sentences(text_only)
            text_only = re.sub(r'  +', ' ', text_only).strip()
            self.num += 1
            return text_only
        except BaseException as e:
            print('Error found in Paragraph', self.num)
            print('Content')
            print(latex_original_paragraph)
            raise e


    def translate_full_latex(self, latex_original, make_complete=True, nocache=False):
        self.add_cache = (not nocache)
        if self.add_cache:
            cache.remove_extra()
            self.hash_key = cache.deterministic_hash((latex_original,  mularg_command_list))
            if cache.is_cached(self.hash_key):
                print('Cache is found')
            cache.create_cache(self.hash_key)

        self.nbad = 0
        self.ntotal = 0

        latex_original = latex_process.remove_tex_comments(latex_original)
        latex_original = latex_original.replace(r'\mathbf', r'\boldsymbol')

        latex_original = latex_process.remove_bibnote(latex_original)
        latex_original = latex_process.process_newcommands(latex_original)

        latex_original = latex_process.replace_accent(latex_original)
        latex_original = latex_process.replace_special(latex_original)

        self.complete = latex_process.is_complete(latex_original)
        self.theorems = latex_process.get_theorems(latex_original)

        if self.complete:
            print('It is a full latex document')
            latex_original, tex_begin, tex_end = latex_process.split_latex_document(latex_original, r'\begin{document}',
                                                                                    r'\end{document}')
            tex_begin = latex_process.remove_blank_lines(tex_begin)
            tex_begin = latex_process.insert_macro(tex_begin, '\\usepackage{xeCJK}\n\\usepackage{amsmath}')


        else:
            print('It is not a full latex document')
            latex_original = text_process.connect_paragraphs(latex_original)

            if make_complete:
                tex_begin = default_begin
                tex_end = default_end
            else:
                tex_begin = ''
                tex_end = ''


        latex_original_paragraphs = self.split_latex_to_paragraphs(latex_original)

        self.num = 0
        # tqdm with concurrent.futures.ThreadPoolExecutor()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            latex_translated_paragraphs = list(tqdm.auto.tqdm(executor.map(self.worker, latex_original_paragraphs),
                                                              total=len(latex_original_paragraphs)))

        latex_translated = '\n\n'.join(latex_translated_paragraphs)
        latex_translated = re.sub(r'\\?XMATHXBS[\s.,;:!?(){}]*', '', latex_translated)
        latex_translated = re.sub(r'\\?XMATHXSP[\s.,;:!?(){}]*', '', latex_translated)

        return latex_translated




def process_latex_file(input, output):

    input_encoding = get_file_encoding(input)

    with open(input, encoding=input_encoding) as f:
        text_original = f.read()

    translator = LatexTranslator()
    text_final = translator.translate_full_latex(text_original)

    text_cleaned = re.sub(r'\n\s*\n+', '\n', text_final)
    text_cleaned = re.sub(r'[ \t]+', ' ', text_cleaned)
    text_cleaned = text_cleaned.strip()


    with open(output, 'w', encoding='utf-8') as f:
        f.write(text_cleaned)

    print(f" processing completed, result saved to {output}")







