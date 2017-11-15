import React from 'react';
import styles from './index.less';
import {connect} from 'dva';
import {Select, Table, Spin} from 'antd';

import {get} from 'lodash'
const Option = Select.Option;

import RevertTable from '../../../../../../components/RevertTable'

function Preview({preview, model, dispatch, namespace}) {

  const {
    stagingDataList,
    table,
    spinLoading: {
      fetchTable
    }
  } = preview;

  const {
    focusSectionsId,
    sectionsJson,
    mouseOverField,
  } = model;

  let fields;
  let labelFields;
  if(!focusSectionsId.includes('new_launcher')){
    // fields = sectionsJson[focusSectionsId].steps[1].args[0].values;
    fields = get(sectionsJson[focusSectionsId], 'steps[1].args[0].values', []);
    // if(namespace === 'modelling'){}
    labelFields = get(sectionsJson[focusSectionsId], 'steps[2].args[0].values', []);
  }

  function handleChange(value) {
    dispatch({
      type: 'preview' + '/fetchTable',
      payload: {_id: value}
    });
  }

  function handleFocus() {

  }

  function handleBlur() {

  }

  let dataSource = null;

  if (table.length !== 0) {
    dataSource = table.data.map((e, index) => {
      return {
        key: index,
        ...e
      }
    })
  }


  let columns = null;
  if (table.length !== 0) {
    columns = table.columns.map((e, index) => {
      const ret = {
        title: <div className={styles.table_title}>
          <div className={styles.table_title_name}>
            {e[0]}
          </div>
          <div className={styles.table_title_type}>
            {e[1][0]}
          </div>
        </div>,
        dataIndex: e[0],
        key: e[0],
        width: 120,
        // styles: {'backgroundColor': "red"}
      };
      let className = '';

      if(fields&&fields.includes(e[0])){
        className += ' active-table-column';
      }

      if(labelFields&&labelFields.includes(e[0])){
        className += ' active-table-column-label';
      }

      if(mouseOverField===e[0]){
        className += ' mouse-over-table-column';
        ret['fixed'] = true;
      }
      ret['className'] = className;
      return ret
    })
  }


  return (
    <div >
      <Spin spinning={fetchTable}>
      <div className={styles.first_line}>
        <Select
          // key={arg.name + argIndex}
          className='column'
          showSearch
          style={{width: 200}}
          placeholder="Select a stagingData"
          optionFilterProp="children"
          onChange={(value) => handleChange(value)}
          onFocus={handleFocus}
          onBlur={handleBlur}
          // defaultValue={arg.values[0]}
          filterOption={(input, option) => option.props.children.toLowerCase().indexOf(input.toLowerCase()) >= 0}
        >
          {stagingDataList.map((stagingData) =>
            <Option key={stagingData._id} value={stagingData._id}>{stagingData.name}</Option>
          )}
        </Select>
      </div>

      {
        dataSource?<div className={styles.info_box}>
          {`${table.row} rows, ${table.col} columns`}
        </div>:null
      }

        <Table dataSource={dataSource} columns={columns} scroll={{ x: 6000 , y: '100%'}}/>
        <RevertTable table={table} fields={fields} labelFields={labelFields}/>
      </Spin>
    </div>
  );
}

export default connect(({preview}) => ({preview}))(Preview);
