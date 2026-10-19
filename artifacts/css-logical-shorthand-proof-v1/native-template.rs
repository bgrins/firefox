pub fn longhands(self) -> NonCustomPropertyIterator<LonghandId> {
        static MAP: [&[LonghandId]; property_counts::SHORTHANDS] = [
        % for property in data.shorthands:
            &[
                % for sub in property.sub_properties:
                    LonghandId::${sub.camel_case},
                % endfor
            ],
        % endfor
        ];
        NonCustomPropertyIterator {
            filter: NonCustomPropertyId::from(self).enabled_for_all_content() &&
                !self.allows_disabled_subproperties(),
            iter: MAP[self as usize].iter(),
        }
    }

pub fn idl_name_sort_order(self) -> u32 {
        <%
            from data import to_idl_name
            ordered = {}
            sorted_shorthands = sorted(data.shorthands, key=lambda p: to_idl_name(p.ident))
            for order, shorthand in enumerate(sorted_shorthands):
                ordered[shorthand.ident] = order
        %>
        static IDL_NAME_SORT_ORDER: [u32; property_counts::SHORTHANDS] = [
            % for property in data.shorthands:
            ${ordered[property.ident]},
            % endfor
        ];
        IDL_NAME_SORT_ORDER[self as usize]
    }