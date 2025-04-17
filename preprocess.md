1. 数据清洗（Filter Node）
    剔除无效或噪声节点:
        ID 为空、仅含乱码或引号的节点（如 "âvictimâ", "â8â", "âŠâ" 等），只保留有明确 type 字段且 id 可解析为企业、组织、个人或地点的记录
    聚焦高风险主体:
        公司（company）：往往是资金往来主体
        政治组织（political_organization）：可能涉及洗钱或利益输送
        个人（person）：可追踪到最终受益人
        其余类型（如纯粹的 string 标签或非实体标签）可暂时过滤

2. 关系筛选（Filter Link）
    重点关注的关系类型:
        ownership（所有权）
        partnership（合伙）
        family_relationship（家族/亲属关系）
        membership（成员身份）
    设置权重阈值:
        仅保留 weight ≥ 0.9 的边，代表极高可信度的关联。例如，ownership 权重大多在 0.92 以上，暗示资金控制链

3. 可疑子图示例
    下表列出了筛选后最可能关联非法交易的几条边及其节点属性：

    | Relationship Type    | Source     | Source Type | Country (if any) | Target                   | Target Type   | Weight  |
    |----------------------|------------|-------------|-------------------|--------------------------|---------------|---------|
    | ownership            | 143129355  | org         | —                 | Spanish Shrimp Carriers  | company       | 0.9217  |
    | ownership            | 12744      | org         | —                 | Spanish Shrimp Carriers  | company       | 0.9170  |
    | family_relationship  | 7775       | org         | —                 | Sean Vasquez             | person        | 0.9461  |
    | family_relationship  | 7775       | org         | —                 | 196159                   | org           | 0.8523  |
    | partnership         | 12744      | org         | —                 | “255–273”                | (string)      | 0.9258  |

    “Spanish Shrimp Carriers”：位于 Nalakond，背后有两个组织（ID 12744、143129355）以 >0.91 权重控股，极可能是资金操盘实体。
    组织 7775 与 Sean Vasquez（person）存在 0.946 的亲属关系，又与另一些组织有 >0.85 的家族链，提示可能的资金输送网。
    ID 为 “255–273” 的奇异字符串，作为 partnership 目标，需进一步核查这可能是交易文档号或暗号。

4. 后续深入分析建议
    跨境流向:
        将公司节点的 country 信息与关系边做拼接，筛选“不同国家间”且高权重的 ownership/partnership
        跨境资金异常往往是洗钱高危信号
    路径追踪:
        在上一步过滤出的子图里，找出“公司→组织→个人→公司”这类多跳路径，识别资金流转链
        对权重大、跳数短的路径优先排查
    可视化:
        使用工具（如 Gephi、Neo4j Bloom）把上述子图绘出，并根据权重高低用粗细或颜色标注，直观发现“重点可疑链”
    属性补全:
        对关键节点（如 12744、143129355、7775）尝试从外部数据库补全注册地、实际控制人、交易记录等，验证其可疑性