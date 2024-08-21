import re

def extract_links_from_file(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
        
        links = []
        for line in lines:
            match = re.search(r"'(https://www\.ximalaya\.com/sound/\d+)'", line)
            if match:
                links.append(match.group(1))
        
        with open(output_file, "w", encoding="utf-8") as outfile:
            for link in links:
                outfile.write(link + "\n")
        
        print(f"成功处理文件，提取到 {len(links)} 个链接，并写入到 {output_file}")
    except Exception as e:
        print(f"处理文件失败：{e}")

if __name__ == "__main__":
    input_file = "res.txt"
    output_file = "processed_album_urls.txt"
    extract_links_from_file(input_file, output_file)
