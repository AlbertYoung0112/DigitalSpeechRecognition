import os
import sys
lib_path = os.path.abspath(os.path.join(sys.path[0], '..'))
sys.path.append(lib_path)
from src.Classifier import Classifier
from src.PreProcessing import PreProcessing
import numpy as np

classifier_classes = Classifier.classifier_dict()
abspath = os.path.abspath(sys.path[0])
CONFIG = {
    'frame size': 512,
    'overlap': 128,
    'is training': True,
    'is streaming': True,
    'data list': '../DataSet/DataList_all.txt',
    'classifier': ['all'],
    'argumentation': False
}


def main():
    preprocessor = PreProcessing(frame_size=CONFIG['frame size'],
                                 overlap=CONFIG['overlap'])
    if CONFIG['is streaming']:
        try:
            preprocessor_proc, queue_dict = preprocessor.process_stream()
            preprocessor_proc.start()
            preprocessor.recorder.start_streaming()
            while True:
                zcr = queue_dict['energy'].get(True)
                ep = queue_dict['endpoint'].get(True)
                mfcc = queue_dict['mfcc'].get(True)
                effective_feature = preprocessor.effective_feature(zcr, ep)
                effective_mfcc = preprocessor.effective_feature(mfcc, ep)
                print("HERE:", effective_mfcc.shape, effective_feature.shape)
                if len(effective_mfcc) == 0:
                    continue
                effective_mfcc = effective_mfcc.reshape((effective_mfcc.shape[0], -1, 1))
                print("HERE again:", effective_mfcc.shape, effective_feature.shape)
                effective_feature = preprocessor.reshape(effective_feature, 100)
                effective_mfcc = preprocessor.reshape(effective_mfcc, 100)
                for classifier_name, classifier_class in classifier_classes.items():
                    print(classifier_name)
                    classifier = classifier_class(None)
                    print(1234)
                    res = classifier.apply(effective_mfcc)
                    print(res)
        except KeyboardInterrupt:
            print('Exit')
        except Exception as e:
            print("Fucking", e)
            print("Emmmmm")
        finally:
            preprocessor_proc.terminate()
            del preprocessor
            exit()
    else:
        wav_list, frame_list, mfcc_list, energy_list, \
        zcr_list, endpoint_list, label_list = preprocessor.process(CONFIG['data list'])
        print('Data set Size:', len(wav_list))
        eff_zcr_list = np.zeros((1, 100))
        eff_mfcc_list = np.zeros((1, 100))
        eff_label_list = []
        # Todo: Rewrite the relating preprocessor code.
        # Multiple data type mixed. Change the list of np array to pure np array.
        #for i in range(len(energy_list)):
        #    temp = preprocessor.effective_feature(zcr_list[i], endpoint_list[i])
        #    temp = preprocessor.reshape(temp, 100)
        #    if len(temp) != 0:
        #        eff_label_list.append(label_list[i])
        #    else:
        #        continue
        #    eff_zcr_list = np.concatenate((eff_zcr_list, temp), axis=0)
        #eff_zcr_list = eff_zcr_list[1:]

        for i in range(len(energy_list)):
            temp = preprocessor.effective_feature(mfcc_list[i], endpoint_list[i]).reshape((1, -1))
            temp = preprocessor.reshape(temp, 100)
            if len(temp) != 0:
                eff_label_list.append(label_list[i])
            else:
                continue
            eff_mfcc_list = np.concatenate((eff_mfcc_list, temp), axis=0)
        eff_mfcc_list = eff_mfcc_list[1:]

        if CONFIG['argumentation']:
            # Todo: Add data argumentation
            raise NotImplementedError
        if 'all' in CONFIG['classifier']:
            for classifier_name, classifier_class in classifier_classes.items():
                if CONFIG['is training']:
                    # Todo: Print training result and validation result
                    # Todo: Save the model to a dir.
                    print(classifier_name)
                    classifier = classifier_class(None)
                    print(len(eff_mfcc_list), len(eff_label_list))
                    classifier.train(eff_mfcc_list, eff_label_list)


if __name__ == '__main__':
    main()
