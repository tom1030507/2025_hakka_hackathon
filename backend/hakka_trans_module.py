import requests
import json
from dotenv import load_dotenv
import os
import re

load_dotenv()

def protect_markdown_symbols(text):
    """
    保護 Markdown 格式符號，避免翻譯時被破墮
    使用特殊 Unicode 字符作為保護符號，避免與 Markdown 格式衝突
    """
    protected_text = text
    
    # 第1步：保護代碼塊佔位符（最高優先級）
    protected_text = re.sub(r'__CODE_BLOCK_(\d+)__', r'❤CODE_BLOCK_\1❤', protected_text)
    protected_text = re.sub(r'__TRANSLATE_PLACEHOLDER_(\d+)__', r'❤TRANSLATE_PLACEHOLDER_\1❤', protected_text)
    
    # 第2步：保護粗體格式 **text**
    protected_text = re.sub(r'\*\*(.+?)\*\*', r'♥BOLD_START♥\1♥BOLD_END♥', protected_text)
    
    # 第3步：保護底線粗體 __text__（避免與代碼塊佔位符衝突）
    protected_text = re.sub(r'(?<!\w)__(.+?)__(?!\w)', r'♦UNDER_BOLD_START♦\1♦UNDER_BOLD_END♦', protected_text)
    
    # 第4步：保護斜體格式 *text* 和 _text_
    # 更精確的斜體匹配，避免與已處理的粗體衝突
    protected_text = re.sub(r'(?<!♥)(?<!\*)\*([^*♥\s][^*♥]*?[^*♥\s])\*(?!\*)(?!♥)', r'♣ITALIC_START♣\1♣ITALIC_END♣', protected_text)
    protected_text = re.sub(r'(?<!♦)(?<!♠)(?<!\w)_([^_♦♠\s][^_♦♠]*?[^_♦♠\s])_(?!\w)(?!♦)(?!♠)', r'♠UNDER_ITALIC_START♠\1♠UNDER_ITALIC_END♠', protected_text)
    
    return protected_text

def restore_markdown_symbols(text):
    """
    恢復 Markdown 格式符號
    增強魯棒性，處理翻譯API可能造成的符號破壞
    """
    restored_text = text
    
    # 第1階段：嘗試恢復完整的符號組合
    # 恢復代碼塊佔位符（最高優先級）
    restored_text = re.sub(r'❤CODE_BLOCK_(\d+)❤', r'__CODE_BLOCK_\1__', restored_text)
    restored_text = re.sub(r'❤TRANSLATE_PLACEHOLDER_(\d+)❤', r'__TRANSLATE_PLACEHOLDER_\1__', restored_text)
    
    # 恢復粗體格式
    restored_text = re.sub(r'♥BOLD_START♥(.+?)♥BOLD_END♥', r'**\1**', restored_text)
    
    # 恢復底線粗體
    restored_text = re.sub(r'♦UNDER_BOLD_START♦(.+?)♦UNDER_BOLD_END♦', r'__\1__', restored_text)
    
    # 恢復斜體格式
    restored_text = re.sub(r'♣ITALIC_START♣(.+?)♣ITALIC_END♣', r'*\1*', restored_text)
    restored_text = re.sub(r'♠UNDER_ITALIC_START♠(.+?)♠UNDER_ITALIC_END♠', r'_\1_', restored_text)
    
    # 第2階段：修復被空格分離的符號
    # 修復被空格分離的粗體符號（包括插入底線的情況）
    restored_text = re.sub(r'♥\s*BOLD\s*_?\s*START\s*♥', '**', restored_text)
    restored_text = re.sub(r'♥\s*BOLD\s*_?\s*END\s*♥', '**', restored_text)
    
    # 修復被空格分離的底線粗體符號
    restored_text = re.sub(r'♦\s+UNDER\s*_?\s*BOLD\s*_?\s*START\s+♦', '__', restored_text)
    restored_text = re.sub(r'♦\s+UNDER\s*_?\s*BOLD\s*_?\s*END\s+♦', '__', restored_text)
    
    # 修復被空格分離的斜體符號
    restored_text = re.sub(r'♣\s+ITALIC\s*_?\s*START\s+♣', '*', restored_text)
    restored_text = re.sub(r'♣\s+ITALIC\s*_?\s*END\s+♣', '*', restored_text)
    
    # 修復被空格分離的底線斜體符號
    restored_text = re.sub(r'♠\s+UNDER\s*_?\s*ITALIC\s*_?\s*START\s+♠', '_', restored_text)
    restored_text = re.sub(r'♠\s+UNDER\s*_?\s*ITALIC\s*_?\s*END\s+♠', '_', restored_text)
    
    # 修復被空格分離的代碼塊符號（包括各種破壞情況）
    restored_text = re.sub(r'❤\s*CODE\s*_?\s*BLOCK\s*_?\s*(\d+)\s*❤', r'__CODE_BLOCK_\1__', restored_text)
    restored_text = re.sub(r'❤\s*CODE\s+BLOCK\s*_?\s*(\d+)\s*❤', r'__CODE_BLOCK_\1__', restored_text)
    restored_text = re.sub(r'❤\s*TRANSLATE\s*_?\s*PLACEHOLDER\s*_?\s*(\d+)\s*❤', r'__TRANSLATE_PLACEHOLDER_\1__', restored_text)
    
    # 第3階段：修復被部分破壞的符號（字母被分離）
    # 修復 "B OLD" -> "BOLD" 等情況
    restored_text = re.sub(r'♥\s*B\s+OLD\s*_?\s*START\s*♥', '**', restored_text)
    restored_text = re.sub(r'♥\s*B\s+OLD\s*_?\s*END\s*♥', '**', restored_text)
    
    # 修復 "C ODE" -> "CODE" 等情況
    restored_text = re.sub(r'❤\s*C\s+ODE\s*_?\s*BLOCK\s*_?\s*(\d+)\s*❤', r'__CODE_BLOCK_\1__', restored_text)
    
    # 修復 "I TALIC" -> "ITALIC" 等情況
    restored_text = re.sub(r'♣\s*I\s+TALIC\s*_?\s*START\s*♣', '*', restored_text)
    restored_text = re.sub(r'♣\s*I\s+TALIC\s*_?\s*END\s*♣', '*', restored_text)
    
    # 第4階段：清理普通的Markdown格式破壞
    # 修復被分離的星號
    restored_text = re.sub(r'\*\s+\*', '**', restored_text)
    # 修復被分離的底線
    restored_text = re.sub(r'_\s+_', '__', restored_text)
    # 修復被分離的代碼塊標記
    restored_text = re.sub(r'_\s+_\s*CODE\s*_\s*BLOCK\s*_\s*(\d+)\s*_\s+_', r'__CODE_BLOCK_\1__', restored_text)
    
    # 第5階段：特殊的中文數字轉換和代碼塊修復
    # 先創建中文數字對應表
    chinese_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '十一': '11', '十二': '12'
    }
    
    # 處理各種被破壞的代碼塊格式
    # 1. 處理中文數字的代碼塊：❤CODE BLOCK_二 ❤ -> __CODE_BLOCK_2__
    for chinese, arabic in chinese_numbers.items():
        restored_text = re.sub(f'❤\s*CODE\s+BLOCK\s*_?\s*{chinese}\s*❤', f'__CODE_BLOCK_{arabic}__', restored_text)
        restored_text = re.sub(f'❤\s*CODE\s*_?\s*BLOCK\s*_?\s*{chinese}\s*❤', f'__CODE_BLOCK_{arabic}__', restored_text)
    
    # 2. 處理被破壞的特殊格式：❤CODE _BLOCK_四 ❤
    for chinese, arabic in chinese_numbers.items():
        restored_text = re.sub(f'❤\s*CODE\s+_\s*BLOCK\s*_?\s*{chinese}\s*❤', f'__CODE_BLOCK_{arabic}__', restored_text)
        restored_text = re.sub(f'❤\s*CODE\s*_\s*BLOCK\s*_?\s*{chinese}\s*❤', f'__CODE_BLOCK_{arabic}__', restored_text)
    
    # 3. 處理其他破墮格式
    restored_text = re.sub(r'❤\s*CODE\s*BLOCK\s*(\d+)\s*❤', r'__CODE_BLOCK_\1__', restored_text)
    restored_text = re.sub(r'❤\s*CODE\s+BLOCK\s*(\d+)\s*❤', r'__CODE_BLOCK_\1__', restored_text)
    
    # 4. 處理不完整的代碼塊格式：CODE_BLOCK_n -> __CODE_BLOCK_n__
    restored_text = re.sub(r'CODE_BLOCK_(\d+)', r'__CODE_BLOCK_\1__', restored_text)
    
    # 5. 處理中文數字的不完整格式：CODE_BLOCK_中文數字 -> __CODE_BLOCK_n__
    for chinese, arabic in chinese_numbers.items():
        restored_text = re.sub(f'CODE_BLOCK_{chinese}', f'__CODE_BLOCK_{arabic}__', restored_text)
    
    # 6. 處理多重底線的情況：____CODE_BLOCK_n____ -> __CODE_BLOCK_n__
    restored_text = re.sub(r'_{3,}CODE_BLOCK_(\d+)_{3,}', r'__CODE_BLOCK_\1__', restored_text)
    
    # 7. 處理中文數字的多重底線情況
    for chinese, arabic in chinese_numbers.items():
        restored_text = re.sub(f'_{3,}CODE_BLOCK_{chinese}_{3,}', f'__CODE_BLOCK_{arabic}__', restored_text)
    
    # 最後的清理，移除任何殘留的保護符號
    unicode_symbols = ['❤', '♥', '♦', '♣', '♠']
    for symbol in unicode_symbols:
        if symbol in restored_text:
            # 記錄警告但不中斷處理
            print(f"⚠️  警告：發現未處理的保護符號 {symbol}")
    
    # 第6階段：最終的 Markdown 格式清理
    # 修復粗體格式中的多餘空格（包括不對稱空格）
    # 1. 兩邊都有空格：** 文字 ** -> **文字**
    restored_text = re.sub(r'\*\*\s+(.+?)\s+\*\*', r'**\1**', restored_text)
    # 2. 左邊有空格：** 文字** -> **文字**
    restored_text = re.sub(r'\*\*\s+(.+?)\*\*', r'**\1**', restored_text)
    # 3. 右邊有空格：**文字 ** -> **文字**
    restored_text = re.sub(r'\*\*(.+?)\s+\*\*', r'**\1**', restored_text)
    
    # 修復底線粗體格式中的多餘空格（包括不對稱空格）
    restored_text = re.sub(r'__\s+(.+?)\s+__', r'__\1__', restored_text)
    restored_text = re.sub(r'__\s+(.+?)__', r'__\1__', restored_text)
    restored_text = re.sub(r'__(.+?)\s+__', r'__\1__', restored_text)
    
    # 修復斜體格式中的多餘空格（但不包括粗體 **）
    restored_text = re.sub(r'(?<!\*)\*\s+(.+?)\s+\*(?!\*)', r'*\1*', restored_text)
    restored_text = re.sub(r'(?<!\*)\*\s+(.+?)\*(?!\*)', r'*\1*', restored_text)
    restored_text = re.sub(r'(?<!\*)\*(.+?)\s+\*(?!\*)', r'*\1*', restored_text)
    
    # 修復底線斜體格式中的多餘空格（但不包括底線粗體 __）
    restored_text = re.sub(r'(?<!_)_\s+(.+?)\s+_(?!_)', r'_\1_', restored_text)
    restored_text = re.sub(r'(?<!_)_\s+(.+?)_(?!_)', r'_\1_', restored_text)
    restored_text = re.sub(r'(?<!_)_(.+?)\s+_(?!_)', r'_\1_', restored_text)
    
    return restored_text

def extract_text_segments(markdown_text):
    """
    從 Markdown 文本中提取需要翻譯的文字段落，完整保留格式結構和換行
    返回: (segments_to_translate, template_with_placeholders)
    """
    segments = []
    placeholder_counter = 0
    
    # 保留原始的換行符號，不要替換成其他符號
    result = markdown_text
    
    # 先保護代碼塊和內嵌代碼，避免翻譯
    code_blocks = []
    code_counter = 0
    
    def preserve_code_blocks(match):
        nonlocal code_counter
        placeholder = f"__CODE_BLOCK_{code_counter}__"
        code_blocks.append(match.group(0))
        code_counter += 1
        return placeholder
    
    # 保護代碼塊（三個反引號）
    result = re.sub(r'```[\s\S]*?```', preserve_code_blocks, result)
    # 保護內嵌代碼（單個反引號）
    result = re.sub(r'`[^`\n]+`', preserve_code_blocks, result)
    
    # 處理標題
    def replace_heading(match):
        nonlocal placeholder_counter
        heading_symbols = match.group(1)  # # ## ### 等
        heading_text = match.group(2).strip()
        if heading_text:
            placeholder = f"__TRANSLATE_PLACEHOLDER_{placeholder_counter}__"
            segments.append(heading_text)
            placeholder_counter += 1
            return f"{heading_symbols} {placeholder}"
        return match.group(0)
    
    # 處理標題 (# ## ###)
    result = re.sub(r'^(#{1,6})\s+(.+)$', replace_heading, result, flags=re.MULTILINE)
    
    # 處理列表項目
    def replace_list_item(match):
        nonlocal placeholder_counter
        list_marker = match.group(1)  # - * + • 或 1. 2. 等
        list_text = match.group(2).strip()
        if list_text and not list_text.startswith(('__TRANSLATE_PLACEHOLDER_', '__CODE_BLOCK_')):
            placeholder = f"__TRANSLATE_PLACEHOLDER_{placeholder_counter}__"
            segments.append(list_text)
            placeholder_counter += 1
            return f"{list_marker}{placeholder}"
        return match.group(0)
    
    # 處理無序列表 (支持 -, *, +, • 等符號)
    result = re.sub(r'^(\s*[-*+•]\s+)(.+)$', replace_list_item, result, flags=re.MULTILINE)
    # 處理有序列表
    result = re.sub(r'^(\s*\d+\.\s+)(.+)$', replace_list_item, result, flags=re.MULTILINE)
    
    # 處理引用文字
    def replace_quote(match):
        nonlocal placeholder_counter
        quote_marker = match.group(1)  # >
        quote_text = match.group(2).strip()
        if quote_text and not quote_text.startswith(('__TRANSLATE_PLACEHOLDER_', '__CODE_BLOCK_')):
            placeholder = f"__TRANSLATE_PLACEHOLDER_{placeholder_counter}__"
            segments.append(quote_text)
            placeholder_counter += 1
            return f"{quote_marker} {placeholder}"
        return match.group(0)
    
    # 處理引用塊
    result = re.sub(r'^(>\s*)(.+)$', replace_quote, result, flags=re.MULTILINE)
    
    # 處理一般段落文字（不在以上格式中的文字）
    # 使用按行處理方式，完整保留原始的換行和空行
    lines = result.split('\n')  # 保留原始的換行分隔
    processed_lines = []
    
    for line_index, original_line in enumerate(lines):
        line = original_line.strip()
        
        # 完整保留空行和已處理的行
        if not line or line.startswith(('__TRANSLATE_PLACEHOLDER_', '__CODE_BLOCK_')):
            processed_lines.append(original_line)  # 保留原始行，包括空行
            continue
            
        # 跳過已處理的標題、列表、引用、表格等
        if (line.startswith('#') or 
            re.match(r'^\s*[-*+•]\s+', line) or  # 支持更多列表符號
            re.match(r'^\s*\d+\.\s+', line) or 
            line.startswith('>') or 
            line.startswith('|') or
            re.match(r'^[-=]+$', line) or  # 標題底線
            re.match(r'^\s*$', line)):  # 空行
            processed_lines.append(original_line)  # 保留原始行
            continue
        
        # 處理一般段落文字
        if line and not re.match(r'^[\s\*\-\+=|>]*$', line):  # 不是只有格式符號的行
            placeholder = f"__TRANSLATE_PLACEHOLDER_{placeholder_counter}__"
            segments.append(line)  # 儲存去除空格的文字內容
            placeholder_counter += 1
            # 完整保留原始縮進和格式
            leading_spaces = len(original_line) - len(original_line.lstrip())
            processed_lines.append(' ' * leading_spaces + placeholder)
        else:
            processed_lines.append(original_line)  # 保留原始行
    
    # 重新組合，保留所有原始換行
    result = '\n'.join(processed_lines)
    
    # 恢復代碼塊
    for i, code_block in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return segments, result

def reconstruct_markdown(template, translated_segments):
    """
    將翻譯後的文字段落重新組合成 Markdown 格式
    """
    result = template
    for i, translated_text in enumerate(translated_segments):
        placeholder = f"__TRANSLATE_PLACEHOLDER_{i}__"
        result = result.replace(placeholder, translated_text.strip())
    return result

def hakka_translate(text, index):
    """
    翻譯 Markdown 文檔，保留格式結構
    """
    # Validate environment variables
    url = os.getenv("HAKKA_TRANS_URL_BASE")
    transUrl = os.getenv("HAKKA_TRANS_URL_TRANS")
    username = os.getenv("HAKKA_TRANS_USERNAME")
    password = os.getenv("HAKKA_TRANS_PASSWORD")

    if not url or not transUrl or not username or not password:
        raise ValueError("Missing one or more required environment variables: HAKKA_TRANS_URL_BASE, HAKKA_TRANS_URL_TRANS, HAKKA_TRANS_USERNAME, HAKKA_TRANS_PASSWORD")

    try:
        # 1. 提取需要翻譯的文字段落
        segments_to_translate, markdown_template = extract_text_segments(text)
        
        if not segments_to_translate:
            # 如果沒有需要翻譯的內容，直接返回原文
            return {
                "success": True,
                "translated_text": text,
                "original_segments": [],
                "translated_segments": []
            }
        
        print(f"Found {len(segments_to_translate)} segments to translate:")
        for i, segment in enumerate(segments_to_translate):
            print(f"  Segment {i}: {segment[:50]}...")
        
        # Authenticate and get token
        payload = json.dumps({
            "username": username,
            "password": password,
            "rememberMe": 0
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        token = response.json().get('token')
        if not token:
            raise ValueError("Authentication failed: No token received")
        print(f"Authentication successful, token: {token[:20]}...")

        # 2. 逐段翻譯文字內容
        translated_segments = []
        translation_headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
        
        for i, segment in enumerate(segments_to_translate):
            try:
                print(f"\n🔄 翻譯段落 {i+1}/{len(segments_to_translate)}: '{segment[:50]}{'...' if len(segment) > 50 else ''}' ")
                
                # 在翻譯前保護 Markdown 格式符號
                protected_segment = protect_markdown_symbols(segment)
                print(f"🛡️  保護後: '{protected_segment[:50]}{'...' if len(protected_segment) > 50 else ''}'")
                
                payload = json.dumps({
                    "input": protected_segment
                })
                response = requests.request("POST", transUrl, headers=translation_headers, data=payload, verify=False)
                response.raise_for_status()
                
                translation_result = response.json()
                print(f"📥 原始翻譯 API 響應: {translation_result}")
                
                # 嘗試從不同字段中提取翻譯結果
                translated_text = None
                
                if 'output' in translation_result:
                    translated_text = translation_result['output']
                    print(f"✅ 從 'output' 字段提取: '{translated_text}'")
                elif 'result' in translation_result:
                    translated_text = translation_result['result']
                    print(f"✅ 從 'result' 字段提取: '{translated_text}'")
                elif 'translation' in translation_result:
                    translated_text = translation_result['translation']
                    print(f"✅ 從 'translation' 字段提取: '{translated_text}'")
                else:
                    # 嘗試直接使用返回的字符串
                    translated_text = str(translation_result).strip('"\'')
                    print(f"⚠️  使用字符串轉換: '{translated_text}'")
                
                # 檢查翻譯結果是否為空或無效
                if not translated_text or translated_text.strip() == "" or translated_text.strip() == "null" or translated_text.strip() == "None":
                    print(f"❌ 翻譯結果為空或無效 ('{translated_text}')！保留原文: '{segment}'")
                    translated_text = segment
                elif len(translated_text.strip()) < 3:  # 翻譯結果太短，可能是錯誤
                    print(f"⚠️  翻譯結果太短 ('{translated_text}')，可能有誤！保留原文: '{segment}'")
                    translated_text = segment
                elif translated_text.strip() == segment.strip():
                    print(f"⚠️  翻譯結果與原文相同，可能翻譯失敗")
                    # 即使翻譯失敗，也要恢復格式符號
                    translated_text = restore_markdown_symbols(translated_text)
                else:
                    print(f"✅ 翻譯成功: '{segment[:30]}...' → '{translated_text[:30]}...'")
                    # 恢復 Markdown 格式符號
                    translated_text = restore_markdown_symbols(translated_text)
                    print(f"🔧 恢復格式後: '{translated_text[:50]}{'...' if len(translated_text) > 50 else ''}'")
                
                translated_segments.append(translated_text)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ 網絡請求失敗 - 段落 {i}: {e}")
                print(f"   保留原文: '{segment}'")
                translated_segments.append(segment)
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析失敗 - 段落 {i}: {e}")
                print(f"   保留原文: '{segment}'")
                translated_segments.append(segment)
            except Exception as e:
                print(f"❌ 未知錯誤 - 段落 {i}: {type(e).__name__}: {e}")
                print(f"   保留原文: '{segment}'")
                translated_segments.append(segment)
        
        # 3. 重新組合 Markdown 文檔
        final_translated_text = reconstruct_markdown(markdown_template, translated_segments)
        
        # Save translation result for debugging
        output_dir = 'temp_trans'
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存詳細的翻譯結果
        detailed_result = {
            "success": True,
            "original_text": text,
            "translated_text": final_translated_text,
            "original_segments": segments_to_translate,
            "translated_segments": translated_segments,
            "markdown_template": markdown_template
        }
        
        output_path = os.path.join(output_dir, f'translation_{index}.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_result, f, ensure_ascii=False, indent=4)
        
        print(f"Translation completed successfully. Saved to {output_path}")
        
        # 返回翻譯結果（與前端期望格式匹配）
        return {
            "success": True,
            "translatedText": final_translated_text,  # 前端期望的字段名
            "output": final_translated_text,  # 保留向後兼容性
            "original_segments": segments_to_translate,
            "translated_segments": translated_segments
        }

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    except ValueError as e:
        raise RuntimeError(f"Error: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during translation: {e}")
