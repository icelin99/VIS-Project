<template>
    <div class="filter-panel-container">
        <div class="filter-item">
            <h3>Select Node</h3>
            <div class="checkbox-container">
                <label class="checkbox-item" v-for="node in nodes" :key="node.value">
                    <input type="checkbox" v-model="selectedNodes" :value="node.value">
                    <span>{{ node.label }}</span>
                    <span class="type-color-dot" :style="{ backgroundColor: typeColors[node.value] }"></span>
                </label>
            </div>
        </div>
        <!-- <div class="filter-item">
            <h3>Select Relation</h3>
            <div class="checkbox-container">
                <label class="checkbox-item" v-for="relation in relations" :key="relation.value">
                    <input type="checkbox" v-model="selectedRelations" :value="relation.value">
                    <span>{{ relation.label }}</span>
                </label>
            </div>
        </div> -->
        <div class="filter-item" v-if="mounted">
            <h3>Select Country</h3>
            <el-select
                v-model="selectedCountries"
                multiple
                clearable
                collapse-tags
                :max-collapse-tags="3"
                placeholder="Select countries"
                popper-class="custom-header"
                class="country-select"
                :teleported="false"
                :fit-input-width="true"
                :popper-append-to-body="false"
                :reserve-keyword="false"
                :popperOptions="{
                    modifiers: [
                        {
                            name: 'computeStyles',
                            options: {
                                adaptive: false,
                                gpuAcceleration: false
                            }
                        }
                    ]
                }"
            >
                <template #header>
                    <el-checkbox
                        v-model="checkAll"
                        :indeterminate="indeterminate"
                        @change="handleCheckAll"
                    >
                        All
                    </el-checkbox>
                </template>
                <el-option
                    v-for="country in countries"
                    :key="country.value"
                    :label="country.label"
                    :value="country.value"
                />
            </el-select>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { ElSelect, ElOption, ElCheckbox } from 'element-plus'

export default {
    name: 'FilterPanel',
    components: {
        ElSelect,
        ElOption,
        ElCheckbox
    },
    computed: {
        ...mapState(['originalNodes', 'countries']),
        nodeTypes() {
            return [...new Set(this.originalNodes.map(node => node.type))]
                .filter(Boolean)
                .map(type => ({value: type, label: type}))
        }
    },
    data() {
        return {
            mounted: false,
            selectedNodes: ['person', 'organization'],
            selectedRelations: [],
            selectedCountries: [],
            checkAll: false,
            indeterminate: false,
            typeColors: {
                'person': '#FFB6C1',
                'organization': '#4ECDC4',
                'company': '#45B7D1',
                'political_organization': '#96CEB4',
                'location': '#FFEEAD',
                'vessel': '#D4A5A5',
                'event': '#9B59B6',
                'movement': '#3498DB',
                'unknown': '#95A5A6'
            },
            nodes: [
                { value: 'person', label: 'Person' },
                { value: 'organization', label: 'Organization' },
                { value: 'company', label: 'Company' },
                { value: 'political_organization', label: 'Political Organization' },
                { value: 'location', label: 'Location' },
                { value: 'vessel', label: 'Vessel' },
                { value: 'event', label: 'Event' },
                { value: 'movement', label: 'Movement' },
                { value: 'unknown', label: 'Unknown' },
            ],
            relations: [
                { value: 'membership', label: 'Membership' },
                { value: 'partnership', label: 'Partnership' },
                { value: 'ownership', label: 'Ownership' },
                { value: 'family relationship', label: 'Family Relationship' },
            ]
        }
    },
    mounted() {
        this.$nextTick(() => {
            this.mounted = true;
        });
    },
    watch: {
        selectedNodes() {
            console.log("selectedNodes-------", this.selectedNodes)
            this.handleFilterChange();
        },
        selectedRelations() {
            this.handleFilterChange();
        },
        selectedCountries: {
            handler(val) {
                if (val.length === 0) {
                    this.checkAll = false;
                    this.indeterminate = false;
                } else if (val.length === this.countries.length) {
                    this.checkAll = true;
                    this.indeterminate = false;
                } else {
                    this.indeterminate = true;
                }
                this.handleFilterChange();
            },
            deep: true
        },
        countries: {
            immediate: true,
            handler(newCountries) {
                if (newCountries && newCountries.length > 0) {
                    this.selectedCountries = newCountries.map(country => country.value);
                    this.checkAll = true;
                }
            }
        }
    },
    methods: {
        ...mapActions(['applyFilters']),
        handleCheckAll(val) {
            this.indeterminate = false;
            if (val) {
                this.selectedCountries = this.countries.map(country => country.value);
            } else {
                this.selectedCountries = [];
            }
        },
        handleFilterChange() {
            this.$store.commit('setFilterConditions', {
                nodeTypes: this.selectedNodes,
                countries: this.selectedCountries
            });
            console.log("更新筛选条件", this.selectedNodes, this.selectedCountries)
            this.applyFilters();
        }
    }
}
</script>

<style scoped>
.filter-panel-container {
    height: 100%;
    width: 95%;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 10px;
    padding-right: 10px;
}

.filter-item {
    position: relative;
    width: 100%;
}

h2 {
    font-size: 18px;
    color: #333;
    margin-bottom: 15px;
}

h3 {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

.checkbox-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-align: left;
    margin-bottom: 8px;
    width: 100%;
    overflow-y: auto;
    max-height: 260px;
    padding-right: 10px; /* 为滚动条预留空间 */
}

.checkbox-item {
    display: grid;
    grid-template-columns: 20px 1fr 16px;
    align-items: center;
    gap: 6px;
    width: 100%;
    box-sizing: border-box;
    padding: 4px 6px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s;
    background: #f5f7fa;
}

.checkbox-item:hover {
    background-color: #ecf5ff;
}

.checkbox-item input[type="checkbox"] {
    margin: 0;
    width: 14px;
    height: 14px;
}

.checkbox-item span:not(.type-color-dot) {
    font-size: 12px;
    color: #606266;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 4px;
}

.type-color-dot {
    display: block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-sizing: content-box;
    flex: none;
    justify-self: end;
}

.country-select {
    width: 100%;
    transform: none !important;
    transition: none !important;
}

:deep(.el-select) {
    width: 100%;
}

:deep(.el-select .el-select__tags) {
    max-width: 90%;
    flex-wrap: nowrap;
    overflow: hidden;
}

:deep(.el-select-dropdown.el-popper) {
    max-width: 100%;
    min-width: 100% !important;
    transform: none !important;
    transition: none !important;
}

:deep(.el-select .el-select__wrapper) {
    max-width: 100%;
}

:deep(.custom-header) {
    padding: 4px 8px;
    border-bottom: 1px solid #eee;
    margin-bottom: 4px;
}

:deep(.el-select-dropdown__item) {
    padding: 0 8px;
    height: 28px;
    line-height: 28px;
    font-size: 12px;
}

:deep(.el-select__tags-text) {
    font-size: 12px;
}

:deep(.el-tag) {
    height: 20px;
    line-height: 20px;
    padding: 0 4px;
}
</style>