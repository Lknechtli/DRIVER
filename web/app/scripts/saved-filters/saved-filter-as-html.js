(function () {
    'use strict';

    // Angular filter for  transforming a saved filter object to an HTML representation.
    // Note: if a new filter rule type is implemented, a new case must be added here for display.
    /* ngInject */
    function SavedFilterAsHTML($translate) {
        var searchTextLabel = $translate.instant('SAVED_FILTERS.SEARCH_TEXT');
        var textSearchLabel = $translate.instant('SAVED_FILTERS.TEXT_SEARCH');
        var unknownRuleType = $translate.instant('ERRORS.UNKNOWN_RULE_TYPE');

        // Helper for determining if a value is a number
        function isNumeric(n) {
            return !isNaN(parseFloat(n)) && isFinite(n);
        }

        return function(filterObj, divider) {
            // `divider` text is optional, if unspecified it uses a span containing a pipe
            divider = divider || '<span class="divider">|</span>';

            var htmlBlocks = [];

            _.forOwn(filterObj, function(val, key) {
                // All label keys start with the name of the related object plus a hash.
                // We only want to display what's after that as the label.
                var label = '<b>' + key.split('#')[1] + '</b>: ';

                /* jshint camelcase: false */
                switch(val._rule_type) {
                    case 'containment_multiple':
                    case 'containment':
                        if (val.pattern) {  // If text search
                            htmlBlocks.push(searchTextLabel + ': ' + val.pattern);
                        } else {
                            htmlBlocks.push(label + val.contains.join(', '));
                        }
                        break;
                    case 'intrange':
                        if (!isNumeric(val.min) && !isNumeric(val.max)) {
                            // No min or max are specified, don't display
                        } else {
                            var html = label;
                            if (isNumeric(val.min) && isNumeric(val.max)) {
                                // Both min and max
                                html += val.min + '-' + val.max;
                            } else if (isNumeric(val.min)) {
                                // Only min
                                html += '&gt; ' + val.min;
                            } else {
                                // Only max
                                html += '&lt; ' + val.max;
                            }
                            htmlBlocks.push(html);
                        }

                        break;

                    default:
                        if (key === '__searchText') {
                            htmlBlocks.push('<strong>' + textSearchLabel + ':</strong> ' + val);
                        } else {
                            htmlBlocks.push(unknownRuleType + ': ' + val._rule_type);
                        }
                        break;
                }
                /* jshint camelcase: true */
            });

            return htmlBlocks.join(divider);
        };
    }

    angular.module('driver.savedFilters')
    .filter('savedFilterAsHTML', SavedFilterAsHTML);

})();
