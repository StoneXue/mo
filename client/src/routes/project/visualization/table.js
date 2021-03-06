import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { Table, Icon } from 'antd'
import lodash from 'lodash'

import style from './table.css'

function isInt(n){
  return Number(n) === n && n % 1 === 0;
}

function isFloat(n){
  return Number(n) === n && n % 1 !== 0;
}
const renderText = (text) => {
  if(text instanceof Number) {
    if(isFloat(text)) {
      return text.toFixed(5)
    }
  }
  return text
}

const getColumns = (props) => {
  let line = props.data.table[0]
  let cols = Object.keys(line)
  cols = cols.filter((el) => el !== '_id')
  cols = cols.filter((el) => el !== 'staging_data_set')
  let Columns = cols.map((e) => {
      if (props.data.X_fields.indexOf(e) !== -1) {
        if (props.data.labels[props.data.X_fields.indexOf(e)]) {
          return ({
            title: e,
            dataIndex: e,
            key: e,
            width: 100,
            //fixed: 'right',
            className: style.fields,
            render: text =>
              <div>
                <span style={{ color: 'rgba(192, 149, 122, 1)' }}>{text}</span>
              </div>,
          })
        } else {
          return ({
            title: e,
            dataIndex: e,
            key: e,
            width: 100,
            //fixed: 'right',
            className: style.fields,
            render: text =>
              <div>
                <span>{text}</span>
              </div>,
          })
        }

      } else if (props.data.Y_target && props.data.Y_target.indexOf(e) !== -1) {
        return ({
          title: e,
          dataIndex: e,
          key: e,
          width: 100,
          //fixed: 'right',
          className: style.target,
          render: text =>
            <div>
              <span>
                {text}
              </span>
            </div>,
        })
      } else {
        return ({
          title: e,
          dataIndex: e,
          key: e,
          width: 100,
          //'fixed': 'right'
        })
      }
    },
  )
  return Columns
}

const getData = (props) => {
  let data = props.data.table
  return [data[0], data[1], data[2], data[3]]
}

const getWidth = (props) => {
  let line = lodash.cloneDeep(props.data.table[0])
  let len = Object.keys(line).length
  let length = 100 * len
  console.log(len, length)
  return length
}

export default (props) => {
  //console.log(props);
  return (
    <div style={{ width: '100%' }}>
      <Table size='default'
             scroll={{ x: getWidth(props) }}
             rowKey={record => record._id}
             columns={getColumns(props)}
             dataSource={getData(props)}
             pagination={true}
      />
    </div>
  )
}
