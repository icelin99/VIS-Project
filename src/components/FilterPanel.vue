<template>
    <div class="filter-panel">
        <h2>Filtering data</h2>
        <div class="filter-item">
            <h3>Select Node</h3>
            <div class="checkbox-container">
                <label class="checkbox-item" v-for="node in nodes" :key="node.value">
                    <input type="checkbox" v-model="selectedNodes" :value="node.value">
                    <span>{{ node.label }}</span>
                </label>
            </div>
        </div>
        <div class="filter-item">
            <h3>Select Relation</h3>
            <div class="checkbox-container">
                <label class="checkbox-item" v-for="relation in relations" :key="relation.value">
                    <input type="checkbox" v-model="selectedRelations" :value="relation.value">
                    <span>{{ relation.label }}</span>
                </label>
            </div>
        </div>
        <div class="filter-item">
            <h3>Select Country</h3>
            <select v-model="selectedCountries" multiple class="multi-select">
                <option v-for="country in countries" 
                        :key="country.value" 
                        :value="country.value">
                    {{ country.label }}
                </option>
            </select>
            <div class="selected-count" v-if="selectedCountries.length">
                choose {{ selectedCountries.length }} countries
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FilterPanel',
    data() {
        return {
            selectedNodes: [],
            selectedRelations: [],
            selectedCountries: [],
            // 示例数据，实际使用时替换为真实数据
            nodes: [
                { value: '1', label: 'Person' },
                { value: '2', label: 'organization' },
                { value: '3', label: 'company' },
                { value: '4', label: 'political organization' },
                { value: '5', label: 'location' },
                { value: '6', label: 'vessel' },
                { value: '7', label: 'event' },
                { value: '8', label: 'movement' },
                { value: '9', label: 'unknown' },
            ],
            relations: [
                { value: '1', label: 'membership' },
                { value: '2', label: 'partnership' },
                { value: '3', label: 'ownership' },
                { value: '4', label: 'family relationship' },
            ],
            countries: [
                { value: '1', label: 'USA' },
                { value: '2', label: 'China' },
                { value: '3', label: 'France' }
            ]
        }
    },
    watch: {
        selectedNodes(newVal) {
            this.$emit('select-node', newVal);
        },
        selectedRelations(newVal) {
            this.$emit('select-relation', newVal);
        },
        selectedCountries(newVal) {
            this.$emit('select-country', newVal);
        }
    }
}
</script>


<style scoped>
.filter-panel {
    height: 100%;
}

.filter-item {
    margin: 20px 0;
}

label {
    display: block;
    margin-bottom: 8px;
}

select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.checkbox-container {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
    text-align: left;
}

.checkbox-item {
    display: flex;
    align-items: center;
    width: calc(50% - 4px);
    /* 每行两个选项 */
    padding: 1px;
    cursor: pointer;
}

.checkbox-item:hover {
    background-color: #f0f0f0;
    border-radius: 4px;
}

.checkbox-item input[type="checkbox"] {
    margin-right: 6px;
}

.checkbox-item span {
    font-size: 14px;
}
</style>