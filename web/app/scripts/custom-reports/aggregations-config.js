(function () {
    'use strict';

    /* Builds a list of available aggregations for the rows and columns of custom reports.
     *
     * The time-related options (type: `Time`) are constant.
     * The list is further populated with all available filterable types (type: `Filter`)
     * and all available geographies (type: `Geography`).
     */

    /* ngInject */
    function AggregationsConfig($q, RecordState, RecordSchemaState, GeographyState) {
        var aggregations = [
            {
                label: 'Day of Month',
                value: 'day',
                type: 'Time'
            },
            {
                label: 'Day of Week',
                value: 'week_day',
                type: 'Time'
            },
            {
                label: 'Hour of Day',
                value: 'hour',
                type: 'Time'
            },
            {
                label: 'Month of Year',
                value: 'month',
                type: 'Time'
            },
            {
                label: 'Week of Year',
                value: 'week',
                type: 'Time'
            },
            {
                label: 'Year',
                value: 'year',
                type: 'Time'
            }
        ];
        var initialized = false;

        var svc = {
            getOptions: getOptions,
        };
        return svc;

        function getOptions() {
            if (initialized) {
                return $q.resolve(aggregations);
            } else {
                return RecordState.getSelected()
                    .then(loadFilters)
                    .then(loadGeographies)
                    .then(function() {
                        initialized = true;
                        return aggregations;
                    });
            }
        }

        /**
         * We can only aggregate on enumerated properties. Loops through the schema (at the
         * definition#property level, not recursively) and adds filters for each
         * enumerated property it finds.
         *
         * TODO:  add " || property.format === 'number'" to the condition to enable aggregating
         * numerical properties if/when that's implemented on the back end.
         */
        function loadFilters(recordType) {
            /* jshint camelcase: false */
            return RecordSchemaState.get(recordType.current_schema).then(function(schema) {
            /* jshint camelcase: true */
                _.forEach(schema.schema.definitions, function(definition, defName) {
                    _.forEach(definition.properties, function(property, propName) {
                        if (property.fieldType === 'selectlist') {
                            aggregations.push({
                                label: propName,
                                value: [defName, 'properties', propName].join(','),
                                type: 'Filter'
                            });
                        }
                    });
                });
            });
        }

        // Add the list of geographies availalable to the dropdown aggregation lists
        function loadGeographies() {
            return GeographyState.getOptions().then(function(geographies) {
                _.each(geographies, function(geography) {
                    aggregations.push({
                        label: geography.label,
                        value: geography.uuid,
                        type: 'Geography'
                    });
                });
            });
        }
    }

    angular.module('driver.customReports')
    .service('AggregationsConfig', AggregationsConfig);
})();