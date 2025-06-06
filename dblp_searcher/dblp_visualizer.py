import os
import re
import sys
from collections import Counter
from wordcloud import WordCloud
from PIL import Image

def compress_image_before_loading(wc_path, max_width=1000):
    """使用Pillow压缩图片，降低内存占用"""
    try:
        img = Image.open(wc_path)
        width, height = img.size

        # 计算缩放比例
        if width > max_width:
            scale = max_width / width
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.LANCZOS)  # 高质量缩放

            # 保存临时压缩图
            temp_path = os.path.splitext(wc_path)[0] + "_temp.jpg"
            img.save(temp_path, "JPEG", quality=85)  # 质量可调整
            return temp_path
        return wc_path
    except Exception as e:
        # print(f"图片压缩失败：{str(e)}")
        return wc_path

def generate_wordcloud(text, output_path="assets/wordcloud.png", max_words=300, chunk_size=5000):
    """
    生成词云图，支持大文本处理（已过滤常见介词）

    参数:
        text: 输入文本
        output_path: 输出路径
        max_words: 最大保留词数
        chunk_size: 每批处理的文本大小
    """

    # 增大递归深度
    sys.setrecursionlimit(10000)

    # 创建输出目录
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # 文本长度检查
        text_length = len(text)
        # print(f"输入文本长度: {text_length} 字符")

        # 定义常见英文介词集合（可根据需求调整）
        prepositions = {'in', 'on', 'at', 'by', 'with', 'from', 'to', 'for', 'of',
             'about', 'as', 'into', 'over', 'under', 'before', 'after',
             'during', 'without', 'through', 'between', 'among', 'and', 'a',
             'based', 'network', 'the', 'via', 'learning', 'an', 'or', 'is',
             'are', 'was', 'were', 'be', 'being', 'been', 'have', 'has',
             'had', 'do', 'does', 'did', 'this', 'that', 'these', 'those',
             'not', 'but', 'if', 'then', 'else', 'when', 'where', 'how',
             'why', 'what', 'which', 'who', 'whom', 'its', 'their', 'our',
             'your', 'my', 'me', 'you', 'he', 'she', 'it', 'they', 'we',
             'us', 'him', 'her', 'them', 'up', 'down', 'out', 'off', 'all',
             'any', 'some', 'no', 'none', 'both', 'each', 'every', 'other',
             'such', 'than', 'too', 'very', 'so', 'just', 'only', 'also',
             'here', 'there', 'now', 'then', 'once', 'again', 'more', 'less',
             'most', 'least', 'many', 'much', 'few', 'little', 'own', 'same',
             'another', 'however', 'therefore', 'furthermore', 'nevertheless'}

        # 短文本直接处理（新增过滤逻辑）
        if text_length < chunk_size:
            # 提取小写单词并过滤介词
            chunk_words = re.findall(r'\w+', text.lower())
            filtered_words = [word for word in chunk_words if word not in prepositions]
            # 统计词频并取前max_words
            word_counts = Counter(filtered_words)
            top_words = dict(word_counts.most_common(max_words))
            # 基于词频生成词云
            wc = WordCloud(width=800, height=400, background_color='white', max_words=max_words)
            wc.generate_from_frequencies(top_words)
            wc.to_file(output_path)
            return output_path

        # 大文本分批处理
        # print(f"开始分批处理大文本...")

        # 提取所有单词并计数（过滤介词）
        words = []
        for i in range(0, text_length, chunk_size):
            chunk = text[i:i + chunk_size]
            # 提取小写单词并过滤介词
            chunk_words = re.findall(r'\w+', chunk.lower())
            filtered_words = [word for word in chunk_words if word not in prepositions]
            words.extend(filtered_words)

        # 统计词频
        word_counts = Counter(words)
        top_words = dict(word_counts.most_common(max_words))

        # 基于词频生成词云
        wc = WordCloud(width=800, height=400, background_color='white')
        wc.generate_from_frequencies(top_words)
        wc.to_file(output_path)

        # print(f"词云生成成功，已保存至: {output_path}")

        output_path = compress_image_before_loading(output_path)

        return output_path

    except Exception as e:
        # print(f"错误: 生成词云失败 - {str(e)}")
        import traceback
        traceback.print_exc()

        # 生成错误提示图
        error_wc = WordCloud(width=800, height=400, background_color='white')
        error_wc.generate(f"生成失败: {str(e)[:50]}")
        error_wc.to_file(output_path)
        return output_path