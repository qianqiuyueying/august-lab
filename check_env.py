# -*- coding: utf-8 -*-
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    print(f'总行数: {len(lines)}')
    print('\n前15行内容:')
    for i, line in enumerate(lines[:15], 1):
        print(f'{i:2d}: {line}')
    print('\n检查乱码字符:')
    has_garbled = any('�' in line for line in lines)
    print(f'发现乱码: {has_garbled}')
    if not has_garbled:
        print('✓ 文件编码正确，没有乱码！')
