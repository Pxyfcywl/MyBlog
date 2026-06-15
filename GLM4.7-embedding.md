模型 API
文本嵌入
使用 GLM Embedding 系列模型将文本转换为高维向量表示，用于语义相似性和搜索。


Copy page
POST
/
paas
/
v4
/
embeddings

Try it
Authorizations
​
Authorization
stringheaderrequired
使用以下格式进行身份验证：Bearer

Body
application/json
​
model
enum<string>required
嵌入模型名称，如 embedding-3、embedding-2

Available options: embedding-3, embedding-2 
​
input

string
string
required
输入文本，支持字符串或字符串数组。

embedding-2 的单条请求最多支持 512 个Tokens，数组总长度不得超过8K
embedding-3 的单条请求最多支持 3072 个Tokens，且数组最大不得超过 64 条
​
dimensions
enum<integer>
输出向量维度，Embedding-3 默认 2048，Embedding-2 固定 1024。Embedding-3 支持自定义，可选值：256、512、1024或2048。

Available options: 2048, 1024, 512, 256 
Required range: x >= 1
Response

200

application/json
业务处理成功

文本嵌入响应对象，包含嵌入向量结果、模型信息和 tokens 统计。

​
model
string
模型编码。

​
object
enum<string>
结果类型，目前为 list。

Available options: list 
​
data
object[]
模型生成的数组结果。每个元素为单条文本的嵌入结果对象。

Hide child attributes

​
data.index
integer
结果下标。该嵌入向量对应的输入文本在输入数组中的索引。

​
data.object
enum<string>
结果类型，目前为 embedding。

Available options: embedding 
​
data.embedding
number[]
embedding 的处理结果，返回向量化表征的数组。

​
usage
object
本次模型调用的 tokens 数量统计。

Hide child attributes

​
usage.prompt_tokens
integer
用户输入的 tokens 数量。

​
usage.completion_tokens
integer
模型输出的 tokens 数量。

​
usage.total_tokens
integer
总 tokens 数量。

curl --request POST \
  --url https://open.bigmodel.cn/api/paas/v4/embeddings \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "model": "embedding-3",
  "input": "你好，今天天气怎么样.",
  "dimensions": 2
}
'

{
  "model": "<string>",
  "object": "list",
  "data": [
    {
      "index": 123,
      "object": "embedding",
      "embedding": [
        123
      ]
    }
  ],
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 123,
    "total_tokens": 123
  }
}