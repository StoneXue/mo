import React from 'react'
import { Button, Table, Checkbox, Select, Modal, Icon, Spin, Tag } from 'antd'
import { connect } from 'dva'
import styles from './index.less'

const Option = Select.Option;
const confirm = Modal.confirm;

class DataPreview extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      ...props,
      chk: false,
    }

  }

  getWidth (columns) {
    return 100 * columns.length
  }

  onCheck (event, e) {
    console.log(this.props)

    const sels = this.props.upload.selected
    if (event.target.checked) {
      sels.push(e)
    } else {
      const index = sels.indexOf(e);
      sels.splice(index, 1)
    }
    this.props.dispatch({type: 'upload/setSelected', payload: sels})
    console.log(sels)
    if (sels.length > 0) {
      this.setState(
        {chk: true}
      )
    } else {
      this.setState(
        {chk: false}
      )
    }
  }

  onSelect (value, e) {
    this.props.dispatch({type: 'upload/setField', payload: {[e]: value}})
    console.log(this.props.upload.fields)
  }

  onSave() {
    this.props.dispatch({type: 'upload/submit'})
  }

  showDeleteConfirm = () => {
    const { dispatch } = this.props
    let sels = this.props.upload.selected

    confirm({
      title: 'Are you sure to delete these columns?',
      content: 'The operation will permanently alter your dataset!',
      okText: 'Yes',
      okType: 'danger',
      cancelText: 'No',
      onOk: () => {
        dispatch({ type: 'upload/delCol', payload: sels })
        this.setState({
          chk: false
        })
      },
      onCancel() {
        console.log('Cancel');
      },
    });
  }


  render () {
    const ds = this.props.upload.dataSet
    const dels = this.props.upload.deleted
    const sels = this.props.upload.selected
    const flds = this.props.upload.fields
    const useless = ['data_set', '_id', 'staging_dataset_id']
    let dsColumns
    let old_col
    let new_col
    // console.log(flds)
    if (Array.isArray(ds) && ds.length > 0) {

      dsColumns = Object.keys(ds[0]).filter(
        (el) => !useless.includes(el)
      )
      dsColumns = dsColumns.filter(
        (el) => !dels.includes(el)
      )

      const myHeader = (e) => <div className={styles.myheader}>
        <Checkbox
          onChange={(event) => {this.onCheck(event, e)}}
          checked={sels.includes(e)}
        >{e}
        </Checkbox>

        <Select className={styles.sel} defaultValue={flds[e]} onChange={(value) => {this.onSelect(value, e)}}>
          <Option key="string" value="string">String</Option>
          <Option key="integer" value="integer">Integer</Option>
          <Option key="float" value="float">Float</Option>
        </Select>
      </div>

      old_col = dsColumns.map((e) => ({
          title: myHeader(e),
          width: 100,
          dataIndex: e,
          key: e,
        }),
      )
    }

    return (
      <div>
        <div className={styles.card}>
          <div className={styles.cleft}>
            <p className={styles.ctitle}>{this.props.upload.dataSetName}</p>
            <p className={styles.cdesc}>{this.props.upload.dataSetDesc}</p>
            {this.props.upload.dataSetTags.length > 0 ?
              <div className={styles.tagzone}>
                {this.props.upload.dataSetTags.map((tag) => <Tag key={tag} color="#C1E4F6">
                  <span className={styles.tag}>{tag}</span></Tag>)}
              </div>:null }
          </div>
          <div className={styles.cright}>
            <Button icon="edit"/>
            <Button icon="delete"/>
          </div>
        </div>
        <div className={styles.whole}>
          <div className={styles.info}>
            <div className={styles.left}>
            <p className={styles.title}>File Information</p>
            <div className={styles.desc}>
              <p>{dsColumns.length} columns, 5 rows for preview</p>
            </div>
            </div>
            <div className={styles.center}>
            </div>
            <div className={styles.right}>
              {this.state.chk? <Button
                className={styles.del}
                type="danger" onClick={() => {this.showDeleteConfirm()}}>
                <Icon type="delete"/>Delete Columns
              </Button>:null}
            </div>
          </div>

          <div>
            {this.props.upload.delLoading?<Spin/>:
              <Table style={{ marginTop: 5, width: '100%' }}
                     dataSource={ds.map((e) => ({...e, key: e._id}))}
                     columns={old_col}
                     pagination={false}
                     bordered={true}
                     scroll={{ x: this.getWidth(old_col), y: '100%' }}
              />
            }

          </div>
          <div className={styles.bottom}>
            <Button type="primary" className={styles.btn}
                    loading={this.props.upload.saveLoading}
                    onClick={() => {this.onSave()}}>Save</Button>
          </div>
        </div>
      </div>
    )
  }
}

export default connect(({ upload }) => ({ upload }))(DataPreview)
